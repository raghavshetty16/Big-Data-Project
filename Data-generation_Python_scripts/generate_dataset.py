"""
Suzlon Energy synthetic data generator.
AI-generated code is used to generate the data-generation logic; the actual dataset
is produced by executing this script, satisfying the assignment requirement.
"""
import os
import numpy as np
import pandas as pd
from config import CONFIG

SEED = CONFIG["seed"]
rng = np.random.default_rng(SEED)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "raw_data")
os.makedirs(OUT_DIR, exist_ok=True)

states = ["Gujarat","Tamil Nadu","Rajasthan","Maharashtra","Karnataka",
          "Andhra Pradesh","Madhya Pradesh","Telangana","Odisha","Kerala"]
regions = {"Gujarat":"West","Maharashtra":"West","Rajasthan":"North",
           "Madhya Pradesh":"Central","Tamil Nadu":"South","Karnataka":"South",
           "Andhra Pradesh":"South","Telangana":"South","Odisha":"East","Kerala":"South"}
segments=["C&I","IPP","PSU","Retail"]
segment_p=[0.40,0.30,0.20,0.10]

# ---------------- Dimensions ----------------
models=[]
capacity_choices=[1500,1800,2100,2500,3000,3300,3500,4200,4500]
for i in range(1, CONFIG["num_models"]+1):
    models.append([i, f"Suzlon-M{i:02d}", int(rng.choice(capacity_choices))])
dim_model=pd.DataFrame(models, columns=["model_id","model_name","rated_capacity_kw"])

customer_rows=[]
for i in range(1, CONFIG["num_customers"]+1):
    seg=rng.choice(segments,p=segment_p)
    state=rng.choice(states)
    customer_rows.append([i,f"Customer_{i:05d}",seg,state])
dim_customer=pd.DataFrame(customer_rows, columns=["customer_id","customer_name","segment","state"])

site_rows=[]
for i in range(1, CONFIG["num_sites"]+1):
    state=rng.choice(states)
    wind_class=rng.choice(["High","Medium","Low"],p=[0.35,0.45,0.20])
    site_rows.append([i,f"WindSite_{i:04d}",state,regions[state],wind_class])
dim_site=pd.DataFrame(site_rows, columns=["site_id","site_name","state","region","wind_zone_class"])

dates=pd.date_range(CONFIG["start_date"], CONFIG["end_date"], freq="D")
dim_date=pd.DataFrame({
    "date_id":np.arange(1,len(dates)+1),
    "full_date":dates.date,
    "month":dates.month,
    "quarter":dates.quarter,
    "year":dates.year,
    "fiscal_year":np.where(dates.month>=4,
        dates.year.astype(str)+"-"+(dates.year+1).astype(str),
        (dates.year-1).astype(str)+"-"+dates.year.astype(str)),
    "is_holiday":[1 if d.weekday()==6 else 0 for d in dates]
})

turbine_rows=[]
for i in range(1, CONFIG["num_turbines"]+1):
    site_id=int(rng.integers(1,CONFIG["num_sites"]+1))
    model_id=int(rng.integers(1,CONFIG["num_models"]+1))
    commissioning=pd.Timestamp("2021-01-01")+pd.to_timedelta(int(rng.integers(0,1460)),unit="D")
    turbine_rows.append([i,f"SZL-{2020+i:06d}",site_id,model_id,commissioning.date()])
dim_turbine=pd.DataFrame(turbine_rows,
    columns=["turbine_id","serial_no","site_id","model_id","commissioning_date"])

tech_rows=[]
for i in range(1, CONFIG["num_technicians"]+1):
    tech_rows.append([i,f"Technician_{i:04d}",
                      rng.choice(["West","North","South","East","Central"]),
                      rng.choice(["Junior","Mid","Senior"],p=[.25,.50,.25])])
dim_technician=pd.DataFrame(tech_rows,
    columns=["technician_id","tech_name","region","skill_level"])

# ---------------- Fact: Orders ----------------
customer_seg=dim_customer.set_index("customer_id")["segment"].to_dict()
model_cap=dim_model.set_index("model_id")["rated_capacity_kw"].to_dict()

order_rows=[]
for oid in range(1, CONFIG["num_orders"]+1):
    cid=int(rng.integers(1,CONFIG["num_customers"]+1))
    mid=int(rng.integers(1,CONFIG["num_models"]+1))
    date_id=int(rng.integers(1,len(dates)+1))
    cap=model_cap[mid]
    qty=int(rng.choice([1,2,3,5,8,10],p=[.28,.25,.18,.14,.08,.07]))
    seg=customer_seg[cid]
    factor={"IPP":1.15,"PSU":1.05,"C&I":1.00,"Retail":0.90}[seg]
    price_per_kw=max(40000,rng.normal(62000,6000))
    order_value=max(1e6,cap*qty*price_per_kw*factor)
    order_rows.append([oid,cid,mid,date_id,round(order_value,2),round(cap*qty/1000,2)])
fact_order=pd.DataFrame(order_rows,
    columns=["order_id","customer_id","model_id","date_id","order_value_inr","mw_capacity"])

# ---------------- Fact: Contracts ----------------
contract_rows=[]
for cid in rng.choice(np.arange(1,CONFIG["num_customers"]+1),
                      size=CONFIG["num_contracts"],replace=True):
    date_id=int(rng.integers(1,len(dates)-60))
    value=float(rng.lognormal(mean=np.log(2.5e6),sigma=.55))
    seg=customer_seg[int(cid)]
    base={"IPP":.76,"PSU":.80,"C&I":.72,"Retail":.64}[seg]
    renewed=int(rng.random()<base)
    contract_rows.append([len(contract_rows)+1,int(cid),date_id,round(value,2),renewed])
fact_contract=pd.DataFrame(contract_rows,
    columns=["contract_id","customer_id","date_id","contract_value_inr","renewed_flag"])

# ---------------- Fact: Generation ----------------
site_wind=dim_site.set_index("site_id")["wind_zone_class"].to_dict()
wind_mult={"High":1.18,"Medium":1.0,"Low":0.82}
month_mult={1:.92,2:.88,3:.90,4:.98,5:1.05,6:1.12,
            7:1.20,8:1.22,9:1.15,10:1.05,11:.98,12:.93}
gen_rows=[]
for t in dim_turbine.itertuples(index=False):
    wm=wind_mult[site_wind[t.site_id]]
    cap=model_cap[t.model_id]
    age_factor=max(.94,1-max(0,(2025-pd.Timestamp(t.commissioning_date).year))*0.006)
    turbine_effect=rng.normal(0,0.012)
    for date_id,d in enumerate(dates,start=1):
        seasonal=month_mult[d.month]
        availability=float(np.clip(rng.normal(.965+turbine_effect,.025),.78,.999))
        wind_speed=float(np.clip(rng.normal(7.2*wm*seasonal,1.4),2.0,14.5))
        capacity_factor=np.clip(.18+.028*wind_speed+rng.normal(0,.025),.05,.52)
        energy=cap*24*capacity_factor*availability*age_factor
        uptime=24*availability
        downtime=24-uptime
        gen_rows.append([len(gen_rows)+1,t.turbine_id,t.site_id,date_id,
                         round(float(energy),2),round(availability*100,2),
                         round(wind_speed,2),round(uptime,2),round(downtime,2)])
fact_generation=pd.DataFrame(gen_rows,
    columns=["gen_id","turbine_id","site_id","date_id","energy_kwh",
             "availability_pct","avg_wind_speed_mps","uptime_hours","downtime_hours"])

# ---------------- Fact: Service ----------------
ticket_types=["Preventive","Corrective","Inspection","Emergency"]
ticket_p=[.32,.40,.16,.12]
service_rows=[]
for ticket_id in range(1,CONFIG["num_service_events"]+1):
    turbine_id=int(rng.integers(1,CONFIG["num_turbines"]+1))
    date_id=int(rng.integers(1,len(dates)+1))
    technician_id=int(rng.integers(1,CONFIG["num_technicians"]+1))
    ticket_type=rng.choice(ticket_types,p=ticket_p)
    severity={"Preventive":1,"Inspection":1,"Corrective":2,"Emergency":3}[ticket_type]
    base_hours={1:2.0,2:5.5,3:9.0}[severity]
    downtime=max(.5,float(rng.lognormal(np.log(base_hours),.45)))
    parts_cost=float(rng.lognormal(np.log(18000*severity),.55))
    service_rows.append([ticket_id,turbine_id,date_id,technician_id,
                         round(downtime,2),ticket_type,severity,round(parts_cost,2)])
fact_service=pd.DataFrame(service_rows,
    columns=["ticket_id","turbine_id","date_id","technician_id",
             "downtime_hours","ticket_type","fault_severity_score","parts_cost_inr"])

tables={
    "dim_model":dim_model,"dim_customer":dim_customer,"dim_site":dim_site,
    "dim_date":dim_date,"dim_turbine":dim_turbine,"dim_technician":dim_technician,
    "fact_order":fact_order,"fact_contract":fact_contract,
    "fact_generation":fact_generation,"fact_service":fact_service
}
for name,df in tables.items():
    df.to_csv(os.path.join(OUT_DIR,f"{name}.csv"),index=False)

print("Generated tables:")
for name,df in tables.items():
    print(f"{name:20s} {len(df):,} rows")

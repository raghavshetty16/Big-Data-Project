import os, pandas as pd
from config import CONFIG
raw=os.path.join(os.path.dirname(__file__),"..","raw_data")
expected=["dim_model","dim_customer","dim_site","dim_date","dim_turbine","dim_technician",
          "fact_order","fact_contract","fact_generation","fact_service"]
for name in expected:
    p=os.path.join(raw,f"{name}.csv")
    assert os.path.exists(p), f"Missing {p}"
    df=pd.read_csv(p)
    assert len(df)>0, f"{name} is empty"
print("All expected raw files exist and are non-empty.")
g=pd.read_csv(os.path.join(raw,"fact_generation.csv"))
assert g["availability_pct"].between(0,100).all()
assert (g["energy_kwh"]>=0).all()
assert g.groupby(["turbine_id","date_id"]).size().max()==1
print("Generation grain and value checks passed.")
print("Validation complete.")

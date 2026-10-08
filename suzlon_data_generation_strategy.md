# Suzlon Energy — Synthetic Data Generation Strategy

## 1. Purpose

This document defines the synthetic-data generation strategy for the Modern Data Engineering final group assignment for Suzlon Energy. The generator is scenario-driven: it creates related customers, sites, turbines, orders, O&M contracts, daily generation records and service events rather than independently filling columns with random values.

All datasets are synthetic and are not intended to represent Suzlon Energy's actual confidential operational or financial data.

## 2. Business scope

The implementation follows the final Assignment 1 schema supplied by the group:

### Dimensions
- `dim_model`
- `dim_customer`
- `dim_site`
- `dim_date`
- `dim_turbine`
- `dim_technician`

### Facts
- `fact_order`
- `fact_contract`
- `fact_generation`
- `fact_service`

The main analytical themes are order booking, O&M contract renewal, turbine generation/availability, service downtime and operational performance.

## 3. Entity relationships

- A customer can place many orders.
- A customer can hold multiple O&M contracts over time.
- A site contains multiple turbines.
- Each turbine belongs to one model and one site.
- Each turbine produces one daily generation record.
- Each service ticket belongs to one turbine and one technician.
- Date keys connect facts to the common date dimension.

## 4. Synthetic business assumptions

### Customers

Customer segments are generated with the following approximate mix:
- C&I: 40%
- IPP: 30%
- PSU: 20%
- Retail: 10%

Customers are assigned states from a 10-state synthetic operating footprint. The state distribution is deliberately broad so regional comparisons are possible.

### Sites

Each site receives:
- state
- region
- wind-zone classification

Wind zones:
- High: 35%
- Medium: 45%
- Low: 20%

Wind-zone classification affects generation potential.

### Turbines and models

There are 15 synthetic turbine models with capacities between approximately 1.5 MW and 4.5 MW.

Each of the 1,000 turbines:
- is assigned to one site,
- is assigned to one model,
- receives a commissioning date between 2021 and 2024,
- receives a unique synthetic serial number.

### Daily generation

The grain is one turbine per day.

Generation depends on:
1. turbine rated capacity,
2. site wind-zone quality,
3. monthly seasonality,
4. turbine availability,
5. turbine age,
6. random operational noise.

Availability is generally high but varies around a turbine-specific baseline. Low availability creates downtime.

The generation model therefore preserves a meaningful relationship:

`better wind + higher capacity + higher availability -> higher energy generation`

### Seasonality

A monthly multiplier changes wind/generation potential. The synthetic profile assumes stronger generation in the monsoon/high-wind period and lower generation in relatively weaker periods.

The exact multipliers are synthetic assumptions, not claims about Suzlon's real portfolio.

### Orders

Orders are generated at customer/model/date level.

Order value depends on:
- turbine rated capacity,
- quantity,
- customer segment,
- synthetic price-per-kW variation.

This creates a relationship between MW capacity and order value.

### O&M contracts

Contracts are linked to customers. Contract values follow a log-normal distribution so that most contracts are moderate while a smaller number are larger.

Renewal probability is segment-dependent:
- IPP: 76%
- PSU: 80%
- C&I: 72%
- Retail: 64%

`renewed_flag` is generated probabilistically.

### Service events

Service tickets are linked to turbines and technicians.

Ticket types:
- Preventive
- Corrective
- Inspection
- Emergency

Corrective and emergency events have higher synthetic downtime and severity. Downtime is generated from a log-normal distribution so that a few events are longer than the typical repair.

## 5. Statistical assumptions

The generator uses:
- categorical weighted sampling for segments and operational classifications,
- normal distributions for operational variation,
- log-normal distributions for monetary values and repair durations,
- bounded values for availability, wind speed and capacity factors,
- deterministic random seed for reproducibility.

## 6. Correlations

The generator intentionally creates these relationships:

1. Wind-zone quality affects wind speed and energy generation.
2. Rated turbine capacity affects daily energy potential.
3. Availability affects uptime, downtime and energy.
4. Turbine age modestly reduces generation efficiency.
5. Customer segment influences synthetic contract renewal probability.
6. Service severity influences downtime and parts cost.
7. Order value depends on capacity, quantity and segment.

## 7. Output volumes

The default configuration produces:

| Table | Rows |
|---|---:|
| dim_model | 15 |
| dim_customer | 5,000 |
| dim_site | 300 |
| dim_date | 365 |
| dim_turbine | 1,000 |
| dim_technician | 250 |
| fact_order | 20,000 |
| fact_contract | 6,000 |
| fact_generation | 365,000 |
| fact_service | 30,000 |

The generation fact alone contains 365,000 rows spanning 2025-01-01 to 2025-12-31.

## 8. Configurability

All major volumes and the date range are controlled through `config.py`. The same generator can therefore produce a small development dataset or a larger final dataset without changing the generation logic.

## 9. Reproducibility

A fixed seed is used by default. Changing the seed creates a different synthetic population while preserving the same distributions and relationships.

## 10. Data-quality expectations

The generated data should satisfy:
- unique dimension primary keys,
- unique turbine serial numbers,
- valid foreign-key references,
- valid date IDs,
- availability between 0 and 100,
- non-negative energy, order value, contract value and downtime,
- one generation row per turbine per day.

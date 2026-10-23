# What electrification costs and what riders pay

A reproducible rider-cost model for motorcycle taxis in Nairobi, prepared for the ENERLAC revision. It asks when an electric motorcycle with Battery-as-a-Service (BaaS) costs less than a financed petrol motorcycle, and what swap price would eliminate that advantage.

**These are conditional scenarios, not verified current contracts, operator profit estimates, causal competition effects, or forecasts of adoption.** The operating sample contains only 9 electric riders. Purchase, rental and financing assumptions must not be interpreted as interchangeable offers.

## Start here

Python 3.10 or later is sufficient for the model; no packages or credentials are required.

```bash
python run_analysis.py
python -m unittest discover -s tests -v
```

The first command overwrites generated files in `results/`. To retain another run:

```bash
python run_analysis.py --out results_alternative
```

For figures only, install Matplotlib (`python -m pip install matplotlib`) and run `python make_figures.py`. The manuscript figures are supplied as editable SVG and 300 dpi PNG files. Figure source data are CSV, not hard-coded chart values.

## Change assumptions

Create a JSON file such as `{"swap_fee": 320, "operating_days": 26}` and run `python run_analysis.py --config your_inputs.json --out results_alternative`. Valid names are the fields of `Assumptions` in `model.py`. The named sensitivity suite still applies its own explicit overrides to your new base; inspect `manifest.json` for each case. Published manuscript numbers correspond to the default configuration only.

## What the model compares

1. **ICE_financed:** petrol vehicle at an assumed KES 195,960; 20% down, 25% APR, 24 months.
2. **EV_BaaS_financed:** vehicle price scenario KES 130,000; the same hypothetical financing terms, with separate swap payments. This is not an advertised Spiro finance contract.
3. **EV_BaaS_cash:** KES 130,000 upfront, with continued BaaS access assumed.
4. **EV_BaaS_rental:** KES 270/day for every payment day throughout the horizon. No transfer of ownership is assumed; this is not a verified 60-month contract.

Base operation: 80 km per operating day, 30 operating and 30 payment days/month, 60 months, and 10% annual discount scenario using monthly rate 0.10/12. Base swap assumption: KES 290 per 95 km. Petrol: KES 214/L. All prices remain constant; there is no inflation forecast. Discount rates are sensitivity choices, not measured rider opportunity costs.

**Cash purchase and financing do not imply that the rider owns the battery.** Battery provision/replacement is assumed covered by the fixed swap tariff. Ownership of a replacement battery is never silently assigned to a BaaS rider.

## Main results from the included run

At 80 km/day, modeled five-year present-value expenditure is approximately KES 1,122,227 for financed ICE, 526,566 for financed EV with BaaS, 510,279 for cash EV with BaaS, and 761,509 for continuous rental with BaaS. Savings relative to financed ICE are 53.1%, 54.5%, and 32.1%, respectively. These are **included-cost estimates under stated assumptions**, not comprehensive all-in market quotations.

In the combined adverse scenario, financed EV retains a 17.1% advantage, but continuous rental is 23.0% more expensive than financed ICE. Do not present a scenario count as a probability of savings. The chosen scenarios are not a representative probability sample.

## Data and estimator

Original dataset: Mbutura et al. (2025), https://doi.org/10.17632/nv3rkn24zv.1. The article is https://doi.org/10.1016/j.dib.2025.111805.

Only transition-phase daily files are used. The supplied files contain 108 ICE riders / 1,150 rows and 9 EV riders / 88 rows. This is the file audit, not the full recruited sample. Positive-distance paired records support fuel and ICE maintenance estimates (940 rows / 98 riders), EV maintenance (84 / 8), charging intensity (28 / 4), and swap spending (40 / 4).

For each cost or physical input, the primary estimator is sum(input) / sum(distance) **over the same nonmissing rider-days**. Missing expenditure is not zero. The short-term measures are purchase/charging and spending proxies, not validated lifetime engineering efficiencies. Equal-rider ratios and mean daily ratios are sensitivity estimators.

Daily utilization 60/80/110 km rounds the ICE rider-mean 25th/50th/75th percentiles (62.47/78.04/106.85). This does not make the sample population-representative.

`data/calibration.json` contains only anonymous aggregates and raw CSV hashes. To independently regenerate it, download the original ZIP, then run:

```bash
python calibrate.py --data-zip "/path/to/original-dataset.zip"
python run_analysis.py
```

Do not commit raw data, GPS trajectories or rider identifiers. Obtain original data from its source and observe its reuse terms.

## Files and outputs

| File | Purpose |
|---|---|
| `model.py` | Validated inputs, annuity payment, monthly cash flow, parity tariff and battery budget |
| `calibrate.py` | Raw ZIP to anonymous paired-data aggregates |
| `run_analysis.py` | 51 named scenarios and parameter sweeps |
| `make_figures.py` | Figures from generated CSVs |
| `data/calibration.json` | Audited, reproducible aggregate inputs |
| `ASSUMPTIONS.md` | Source status, modeling boundaries and scenario rationale |
| `results/scenarios.csv` | TCO, initial outlay, monthly burden and conditional savings |
| `results/cashflows.csv` | Every month and cost component for every scenario |
| `results/thresholds.csv` | Swap tariff at which EV and ICE expenditure are equal |
| `results/battery_budgets.csv` | Maximum hypothetical pack-price budget at alternative lives |
| `results/benchmarks.csv` | Electricity-only benchmark and swap spending gap |
| `results/manifest.json` | Full parameters, interpreter version and SHA-256 hashes |
| `tests/test_model.py` | Accounting, parity, missingness and boundary checks |

## Read results correctly

The electricity benchmark is kWh/km times an assumed electricity tariff. Its difference from the swap fee includes unmeasured battery, station, logistics, finance and service components. It is **not a profit margin or an achievable saving from switching to home charging**. Charging and swapping groups differ; there is no causal matching.

A parity tariff is the rider's expenditure break-even price, not the operator's viable tariff or a recommended price cap. Unequal downtime reduces kilometers; those cases deliberately leave total-TCO savings and parity tariffs blank. Compare cost per delivered kilometer and report lost service separately; no income or welfare gains are estimated.

Battery budgets compare hypothetical cash self-charging with cash BaaS while holding nonbattery vehicle costs constant. They allocate the remaining present-value budget to an initial pack and replacements. Actual compatible battery prices, charger costs, access, labor/time and resale value are unknown. This is a feasibility threshold, not an owned-EV TCO estimate.

## Validation and limits

12 automated tests pass. They validate arithmetic and safeguards, not the truth of scenario inputs. The two primary CSV source hashes and calibration reproducibility were checked against the supplied ZIP. Significant limitations include short observation windows, EV n=9, nonrandom charging access, financing eligibility, future prices and aging, unobserved taxes/insurance/registration, residual values, downtime and uncertain current contracts. These costs are excluded at reference values and explored selectively, not assumed universally absent.

No Monte Carlo confidence interval or causal market-concentration result is reported. No inference that subsidies are unimportant follows from one illustrative transfer amount.

## GitHub publication

This directory is prepared as a repository, but this delivery does not claim that a remote repository has been created or pushed. An authenticated GitHub account and destination are required. Create an empty repository, then use GitHub Desktop to add this directory and publish it, or use the commands in `PUBLISH.md`. Keep the manuscript and author details separate from an anonymous review submission. There is no software license grant in this package; choose a license before inviting reuse under specific terms.

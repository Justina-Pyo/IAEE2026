# Assumptions and evidence register

## Source categories

- **Observed:** anonymous aggregates of the supplied 2023 daily data, paired on rider-day.
- **Displayed:** figures visible in Spiro website calculator / purchase screenshots supplied on 6 October 2026; they are not contracts. Screenshots are not redistributed.
- **Inherited scenario:** prior manuscript inputs that lack a verified current quotation.
- **Exploratory:** researcher-selected sensitivity, not an estimated probability distribution.

| Input | Reference | Status and rationale |
|---|---:|---|
| ICE fuel | 0.0293967 L/km | Paired pooled 2023 purchase proxy; tank inventory/timing not observed |
| ICE maintenance | 1.69194 KES/km | Paired pooled; short window does not capture full aging |
| EV maintenance | 0.313954 KES/km | 84 positive-distance records, 8 riders |
| Charging | 0.0467638 kWh/km | 28 positive-distance records, 4 riders; wall-meter input proxy |
| Observed swap spending | 3.54429 KES/km | 40 positive-distance records, 4 other riders |
| ICE price | 195,960 KES | Inherited scenario; not independently verified as October 2026 market price |
| EV vehicle price | 130,000 KES | Displayed starting ex-showroom price; battery ownership/taxes/fees not established |
| Rental | 270 KES/day | Displayed calculator rental; continuous payment throughout horizon is hypothetical |
| Swap | 290 KES / 95 km | 290 inherited scenario; 95 displayed illustrative range, not field efficiency |
| Petrol | 214 KES/L | Displayed calculator input; not represented as official pump-price verification |
| Electricity | 22 KES/kWh | Inherited benchmark scenario, not a verified all-in current tariff; vary 15/35/50 |
| Financing | 20% down, 25% APR, 24 months | Common analytical terms, not a verified offer. Watu advertises up to 24 months; this does not validate the APR/down payment or Spiro offer |
| Discount | 10%; alternatives 25%, 40% | Researcher-selected annual rates with monthly r/12 convention, no measured welfare discount claim |
| Horizon | 60 months; 36/84 alternatives | Evaluation horizon, not evidence of vehicle service life; unchanged operation across years is a strong assumption |
| Days | 30 operating and 30 payment days/month | 360-day normalization; 22/26 operating days tested independently of payment days |
| Distance | 60/80/110 km/day | Rounded rider-level mean quartiles from ICE sample |
| Deposit, taxes, insurance, registration | Excluded unless extras entered | No comprehensive current contract source; omission is a limitation, not proof of zero cost |
| Terminal value | Zero base; 20% purchase-price sensitivity | Exploratory, no rental asset credited |

## Sensitivities

The 51 scenarios include empirical rider maintenance quartiles, leave-one-rider-out pooled estimates, maintenance multipliers 0.5/2, fuel and EV energy-intensity transfer factors 0.8/1.2, illustrative swap ranges 80/95/100 km, swap-price factors 0.8/1.2, independent operating days and downtime 5/10/15%, horizons 3/5/7 years, APR 0/15/25/40%, and loan terms 12/24/36 months. Apart from empirical quantiles and publicly displayed range examples, these are exploratory bounds, not externally validated plausible intervals.

The manufacturer's 45 km/L assumption is tested separately from the 2023 fuel proxy. Its displayed EV monthly maintenance KES 4,002 is also tested at an inferred 80 km/day and 365/12 days/month; this is an alternative calculator assumption, not observed maintenance. The baseline does not use the calculator's advertised savings.

The adverse joint case holds service equal: 60 km/day, 22 operating days/month, 30 rental payment days, ICE fuel intensity 20% lower, ICE maintenance half, EV maintenance double, swap fee 20% higher, range 80 km, and an extra EV upfront KES 30,000. It is not an estimated worst case or likelihood statement.

Hypothetical policy: KES 10,000 support, 50% or 100% rider pass-through. Purchase support reduces vehicle price before computing down payment and principal. Rental support is evenly distributed over the horizon. Different timing produces different present values; this is not an actual tax exemption calculation or a like-for-like fiscal efficiency ranking.

Battery lives 24/36/60 months are exploratory thresholds. Replacement at the terminal month is omitted because it yields no modeled future service. Pack prices are solved for, not assumed observed. Battery deterioration may also reduce swap range or raise tariffs; those channels are tested separately without asserting an empirical mapping.

## Sources

Mbutura, A., Kitetu, M., Stratford, H., & Booysen, M. J. (2025). Nairobi motorcycle transit comparison dataset: Fuel vs. electric vehicle performance tracking (2023). Data in Brief, 61, 111805. https://doi.org/10.1016/j.dib.2025.111805

Dataset: https://doi.org/10.17632/nv3rkn24zv.1

Spiro product and illustrative range pages, checked 15 October 2026: https://www.spironet.com/ekon and https://www.spironet.com/energy . Purchase/calculator screenshots supplied 6 October 2026 provide displayed inputs; a capture date is not a guaranteed effective contract date.

Watu Kenya mobility financing, checked 15 October 2026: https://watu.com/kenya/mobility/ . The public page says up to 24 months but does not establish the hypothetical financing terms used here.

# Lebanon Education Crisis Data: Indicator Metadata

This file provides descriptions for the indicators included in `lebanon_education_data.csv`.

## 📂 Data Sources
- **World Bank (WB):** Economic and broad education statistics.
- **UNESCO UIS:** Detailed education quality and access metrics.
- **UNICEF:** Wellbeing and child-specific indicators.
- **UNHCR:** Refugee and displacement counts.

---

## 📊 Indicators by Category

### 🏫 Education Access & Enrollment
| Code | Label | Unit | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `SE.PRM.ENRR` | Primary enrollment, gross (%) | % | WB | Total enrollment in primary education, regardless of age, as a % of the population of official primary education age. |
| `SE.SEC.ENRR` | Secondary enrollment, gross (%) | % | WB | Total enrollment in secondary education, regardless of age, as a % of the population of official secondary education age. |
| `SE.PRM.UNER.ZS` | Out-of-school children, primary (%) | % | WB | Percentage of children of primary school age who are not in school. |
| `ROFST.1.CP` | Out-of-school rate, primary (%) | % | UIS | UIS-calculated rate of primary-aged children not enrolled in school. |
| `ROFST.2.CP` | Out-of-school rate, lower secondary (%) | % | UIS | UIS-calculated rate of lower-secondary-aged adolescents not enrolled in school. |
| `GER.02` | Gross enrollment ratio, pre-primary (%) | % | UIS | Enrollment in pre-primary education as a % of the population of official pre-primary age. |

### 👩‍🏫 Teachers & Quality
| Code | Label | Unit | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `SE.PRM.ENRL.TC.ZS` | Pupil-teacher ratio, primary | ratio | WB | Number of pupils per teacher in primary education. |
| `SE.SEC.ENRL.TC.ZS` | Pupil-teacher ratio, secondary | ratio | WB | Number of pupils per teacher in secondary education. |
| `SE.PRM.TCAQ.ZS` | Trained teachers, primary (%) | % | WB | Percentage of primary school teachers who have received at least the minimum organized teacher training. |
| `TRTP.1` | Trained teachers, primary (%) | % | UIS | UNESCO-verified percentage of trained primary teachers. |

### 📈 Learning Outcomes
| Code | Label | Unit | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `SE.PRM.CMPT.ZS` | Primary completion rate (%) | % | WB | Percentage of children reaching the last grade of primary education. |
| `SE.ADT.1524.LT.ZS` | Youth literacy rate 15–24 (%) | % | WB | Percentage of people aged 15–24 who can both read and write. |
| `CR.1` | Completion rate, primary (%) | % | UIS | UIS-calculated completion rate for primary education. |

### 💰 Economic & Expenditure
| Code | Label | Unit | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `NY.GDP.PCAP.CD` | GDP per capita (USD) | USD | WB | Gross Domestic Product per person in current US dollars. |
| `FP.CPI.TOTL.ZG` | Inflation (%) | % | WB | Annual percentage change in the cost to the average consumer of acquiring a basket of goods and services. |
| `SE.XPD.TOTL.GD.ZS` | Education expenditure (% of GDP) | % | WB | Public expenditure on education as a percentage of GDP. |
| `SI.POV.DDAY` | Poverty headcount ($2.15/day) (%) | % | WB | Percentage of the population living on less than $2.15 a day (2017 PPP). |

### 🌍 Displacement & Wellbeing
| Code | Label | Unit | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `UNHCR_ALL_REFUGEES_LBN` | Total refugees in Lebanon (count) | count | UNHCR | Total number of refugees residing in Lebanon from all origins. |
| `UNHCR_SYR_REFUGEES_LBN` | Syrian refugees in Lebanon (count) | count | UNHCR | Number of Syrian refugees residing in Lebanon. |
| `CME_MRY0T4` | Under-5 mortality rate | per 1k | UNICEF | Probability of dying between birth and age 5 per 1,000 live births. |

---

## 📅 Historical Context (Breakpoints)
These events are crucial for interpreting sudden shifts in the data:
- **2011:** Syrian civil war begins (Massive refugee influx).
- **2015:** Peak Syrian refugee arrivals.
- **2019:** Lebanese financial collapse (Currency devaluation begins).
- **2020:** COVID-19 pandemic + Beirut Port explosion.
- **2021:** Extreme currency collapse & widespread teacher strikes.
- **2024:** Southern Lebanon war & mass internal displacement.

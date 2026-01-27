# OWID CO2 Dataset - Feature Descriptions

This document describes each column (feature) in `owid-co2-data.csv`, sourced from [Our World in Data](https://github.com/owid/co2-data).

## Identification & Demographics

| Feature | Description |
|---------|-------------|
| `country` | Country or region name |
| `year` | Year of observation |
| `iso_code` | ISO 3166-1 alpha-3 country code |
| `population` | Total population of the country/region |
| `gdp` | Gross domestic product (international-$ using 2011 prices) |

## Total CO2 Emissions

| Feature | Description |
|---------|-------------|
| `co2` | Annual production-based CO2 emissions (million tonnes) |
| `co2_growth_abs` | Annual absolute change in CO2 emissions (million tonnes) |
| `co2_growth_prct` | Annual percentage change in CO2 emissions |
| `co2_per_capita` | Annual CO2 emissions per person (tonnes per person) |
| `co2_per_gdp` | Annual CO2 emissions per unit of GDP (kg per international-$) |
| `co2_per_unit_energy` | Annual CO2 emissions per unit of primary energy (kg per kilowatt-hour) |

## CO2 Including Land-Use Change

| Feature | Description |
|---------|-------------|
| `co2_including_luc` | Annual CO2 emissions including land-use change (million tonnes) |
| `co2_including_luc_growth_abs` | Annual absolute change in CO2 emissions including land-use change (million tonnes) |
| `co2_including_luc_growth_prct` | Annual percentage change in CO2 emissions including land-use change |
| `co2_including_luc_per_capita` | CO2 emissions including land-use change per person (tonnes per person) |
| `co2_including_luc_per_gdp` | CO2 emissions including land-use change per unit of GDP (kg per international-$) |
| `co2_including_luc_per_unit_energy` | CO2 emissions including land-use change per unit of primary energy (kg per kilowatt-hour) |

## CO2 by Source

| Feature | Description |
|---------|-------------|
| `cement_co2` | Annual CO2 emissions from cement production (million tonnes) |
| `cement_co2_per_capita` | CO2 emissions from cement per person (tonnes per person) |
| `coal_co2` | Annual CO2 emissions from coal (million tonnes) |
| `coal_co2_per_capita` | CO2 emissions from coal per person (tonnes per person) |
| `flaring_co2` | Annual CO2 emissions from gas flaring (million tonnes) |
| `flaring_co2_per_capita` | CO2 emissions from flaring per person (tonnes per person) |
| `gas_co2` | Annual CO2 emissions from gas (million tonnes) |
| `gas_co2_per_capita` | CO2 emissions from gas per person (tonnes per person) |
| `oil_co2` | Annual CO2 emissions from oil (million tonnes) |
| `oil_co2_per_capita` | CO2 emissions from oil per person (tonnes per person) |
| `other_industry_co2` | Annual CO2 emissions from other industry sources (million tonnes) |
| `other_co2_per_capita` | CO2 emissions from other industry per person (tonnes per person) |
| `land_use_change_co2` | Annual CO2 emissions from land-use change (million tonnes) |
| `land_use_change_co2_per_capita` | CO2 emissions from land-use change per person (tonnes per person) |

## Consumption-Based CO2

| Feature | Description |
|---------|-------------|
| `consumption_co2` | Annual consumption-based CO2 emissions (million tonnes). Adjusts for trade by adding emissions embedded in imports and subtracting those in exports. |
| `consumption_co2_per_capita` | Consumption-based CO2 emissions per person (tonnes per person) |
| `consumption_co2_per_gdp` | Consumption-based CO2 emissions per unit of GDP (kg per international-$) |
| `trade_co2` | Annual net CO2 emissions embedded in trade (million tonnes). Positive = net importer, negative = net exporter. |
| `trade_co2_share` | Net CO2 emissions embedded in trade as a share of domestic production emissions (%) |

## Cumulative CO2 Emissions

| Feature | Description |
|---------|-------------|
| `cumulative_co2` | Cumulative production-based CO2 emissions (million tonnes) |
| `cumulative_co2_including_luc` | Cumulative CO2 emissions including land-use change (million tonnes) |
| `cumulative_cement_co2` | Cumulative CO2 emissions from cement (million tonnes) |
| `cumulative_coal_co2` | Cumulative CO2 emissions from coal (million tonnes) |
| `cumulative_flaring_co2` | Cumulative CO2 emissions from gas flaring (million tonnes) |
| `cumulative_gas_co2` | Cumulative CO2 emissions from gas (million tonnes) |
| `cumulative_luc_co2` | Cumulative CO2 emissions from land-use change (million tonnes) |
| `cumulative_oil_co2` | Cumulative CO2 emissions from oil (million tonnes) |
| `cumulative_other_co2` | Cumulative CO2 emissions from other industry (million tonnes) |

## Share of Global CO2 (Annual)

| Feature | Description |
|---------|-------------|
| `share_global_co2` | Share of global annual CO2 emissions (%) |
| `share_global_co2_including_luc` | Share of global annual CO2 emissions including land-use change (%) |
| `share_global_cement_co2` | Share of global annual cement CO2 emissions (%) |
| `share_global_coal_co2` | Share of global annual coal CO2 emissions (%) |
| `share_global_flaring_co2` | Share of global annual flaring CO2 emissions (%) |
| `share_global_gas_co2` | Share of global annual gas CO2 emissions (%) |
| `share_global_luc_co2` | Share of global annual land-use change CO2 emissions (%) |
| `share_global_oil_co2` | Share of global annual oil CO2 emissions (%) |
| `share_global_other_co2` | Share of global annual other industry CO2 emissions (%) |

## Share of Global Cumulative CO2

| Feature | Description |
|---------|-------------|
| `share_global_cumulative_co2` | Share of global cumulative CO2 emissions (%) |
| `share_global_cumulative_co2_including_luc` | Share of global cumulative CO2 emissions including land-use change (%) |
| `share_global_cumulative_cement_co2` | Share of global cumulative cement CO2 emissions (%) |
| `share_global_cumulative_coal_co2` | Share of global cumulative coal CO2 emissions (%) |
| `share_global_cumulative_flaring_co2` | Share of global cumulative flaring CO2 emissions (%) |
| `share_global_cumulative_gas_co2` | Share of global cumulative gas CO2 emissions (%) |
| `share_global_cumulative_luc_co2` | Share of global cumulative land-use change CO2 emissions (%) |
| `share_global_cumulative_oil_co2` | Share of global cumulative oil CO2 emissions (%) |
| `share_global_cumulative_other_co2` | Share of global cumulative other industry CO2 emissions (%) |

## Other Greenhouse Gases

| Feature | Description |
|---------|-------------|
| `total_ghg` | Total greenhouse gas emissions including land-use change and forestry (million tonnes CO2 equivalent) |
| `total_ghg_excluding_lucf` | Total greenhouse gas emissions excluding land-use change and forestry (million tonnes CO2 equivalent) |
| `ghg_per_capita` | Total GHG emissions per person including land-use change (tonnes CO2 eq per person) |
| `ghg_excluding_lucf_per_capita` | Total GHG emissions per person excluding land-use change (tonnes CO2 eq per person) |
| `methane` | Total methane emissions (million tonnes CO2 equivalent) |
| `methane_per_capita` | Methane emissions per person (tonnes CO2 eq per person) |
| `nitrous_oxide` | Total nitrous oxide emissions (million tonnes CO2 equivalent) |
| `nitrous_oxide_per_capita` | Nitrous oxide emissions per person (tonnes CO2 eq per person) |

## Energy

| Feature | Description |
|---------|-------------|
| `primary_energy_consumption` | Primary energy consumption (terawatt-hours) |
| `energy_per_capita` | Primary energy consumption per person (kilowatt-hours per person) |
| `energy_per_gdp` | Energy consumption per unit of GDP (kilowatt-hours per international-$) |

## Temperature Change Contributions

| Feature | Description |
|---------|-------------|
| `share_of_temperature_change_from_ghg` | Share of contribution to global warming from all greenhouse gases (%) |
| `temperature_change_from_ghg` | Change in global mean surface temperature caused by all greenhouse gases (degrees Celsius) |
| `temperature_change_from_co2` | Change in global mean surface temperature caused by CO2 emissions (degrees Celsius) |
| `temperature_change_from_ch4` | Change in global mean surface temperature caused by methane emissions (degrees Celsius) |
| `temperature_change_from_n2o` | Change in global mean surface temperature caused by nitrous oxide emissions (degrees Celsius) |

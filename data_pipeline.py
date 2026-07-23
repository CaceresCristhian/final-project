import pandas as pd
import numpy as np
import os
import json

print("=== Starting Data Processing and Integration Pipeline ===")

# Create directory if missing
os.makedirs("data/processed", exist_ok=True)

# ---------------------------------------------------------
# 1. Load and Aggregating Temperature Data (city_temperature.csv)
# ---------------------------------------------------------
print("Loading and cleaning temperature data...")
temp_file = "data/raw/europe_temperatures.csv"

# Since city_temperature.csv is 140MB, we can read it efficiently using Pandas
df_temp = pd.read_csv(temp_file, usecols=['Country', 'Month', 'Day', 'Year', 'AvgTemperature'], low_memory=False)

# Clean and convert Fahrenheit to Celsius
# Filter invalid years (e.g., negative or future years) and invalid AvgTemperature (e.g., -99 from sensor errors)
df_temp = df_temp[(df_temp['Year'] >= 2000) & (df_temp['Year'] <= 2020)]
df_temp = df_temp[df_temp['AvgTemperature'] > -70]  # raw -99.0 indicates missing data
df_temp['TempCelsius'] = (df_temp['AvgTemperature'] - 32) * (5 / 9)

# Define target countries (matching forecast_europe.py)
EUROPEAN_COUNTRIES = [
    'Albania', 'Austria', 'Belarus', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 
    'Czech Republic', 'Denmark', 'Finland', 'France', 'Georgia', 'Germany', 
    'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Macedonia', 
    'Norway', 'Poland', 'Portugal', 'Romania', 'Russia', 'Serbia-Montenegro', 
    'Slovakia', 'Spain', 'Sweden', 'Switzerland', 'The Netherlands', 'Turkey', 
    'Ukraine', 'United Kingdom', 'Yugoslavia'
]

# Filter for European Countries
df_temp = df_temp[df_temp['Country'].isin(EUROPEAN_COUNTRIES)]

# Aggregate to Annual mean temperature per country
print("Aggregating annual temperatures...")
df_annual_temp = df_temp.groupby(['Country', 'Year'])['TempCelsius'].mean().reset_index()
df_annual_temp.rename(columns={'TempCelsius': 'AnnualMeanTemp'}, inplace=True)

# Aggregate to Monthly volatility (standard deviation of monthly averages per year)
print("Computing monthly temperature volatility...")
df_monthly_avg = df_temp.groupby(['Country', 'Year', 'Month'])['TempCelsius'].mean().reset_index()
df_volatility = df_monthly_avg.groupby(['Country', 'Year'])['TempCelsius'].std().reset_index()
df_volatility.rename(columns={'TempCelsius': 'TempVolatility'}, inplace=True)

# Merge temperature metrics
df_temp_metrics = pd.merge(df_annual_temp, df_volatility, on=['Country', 'Year'], how='inner')

# ---------------------------------------------------------
# 2. Load OWID CO2 Dataset (owid-co2-data.csv)
# ---------------------------------------------------------
print("Loading OWID CO2 dataset...")
co2_file = "data/raw/owid-co2-data.csv"
df_co2 = pd.read_csv(co2_file, usecols=['country', 'year', 'iso_code', 'co2', 'co2_per_capita', 'cumulative_co2', 'gdp', 'population', 'total_ghg', 'ghg_per_capita'])

# Calculate gdp_per_capita dynamically
df_co2['gdp_per_capita'] = df_co2['gdp'] / df_co2['population']

# Standardize country mapping to match temperature data
country_mapping = {
    'Netherlands': 'The Netherlands',
    'Czechia': 'Czech Republic',
    'North Macedonia': 'Macedonia',
    'Serbia': 'Serbia-Montenegro'
}
df_co2['country'] = df_co2['country'].replace(country_mapping)
df_co2 = df_co2[df_co2['country'].isin(EUROPEAN_COUNTRIES)]
df_co2.rename(columns={'country': 'Country', 'year': 'Year', 'total_ghg': 'greenhouse_gas'}, inplace=True)

# ---------------------------------------------------------
# 3. Load OWID Energy Dataset (owid-energy-data.csv)
# ---------------------------------------------------------
print("Loading OWID Energy dataset...")
energy_file = "data/raw/owid-energy-data.csv"
df_energy = pd.read_csv(energy_file, usecols=[
    'country', 'year', 'electricity_generation', 'coal_electricity', 'gas_electricity', 
    'nuclear_electricity', 'hydro_electricity', 'solar_electricity', 'wind_electricity', 
    'renewables_electricity', 'low_carbon_electricity', 'carbon_intensity_elec'
])

df_energy['country'] = df_energy['country'].replace(country_mapping)
df_energy = df_energy[df_energy['country'].isin(EUROPEAN_COUNTRIES)]
df_energy.rename(columns={'country': 'Country', 'year': 'Year'}, inplace=True)

# Calculate fuel shares (%)
for source in ['coal', 'gas', 'nuclear', 'hydro', 'solar', 'wind', 'renewables', 'low_carbon']:
    col_name = f'{source}_electricity'
    if col_name in df_energy.columns:
        df_energy[f'{source.capitalize()}Share'] = (df_energy[col_name] / df_energy['electricity_generation']) * 100
        # Clean infinite or NaN values
        df_energy[f'{source.capitalize()}Share'] = df_energy[f'{source.capitalize()}Share'].fillna(0.0).replace([np.inf, -np.inf], 0.0)

# Drop raw electricity generation source columns to save space
cols_to_drop = [c for c in df_energy.columns if c.endswith('_electricity')]
df_energy.drop(columns=cols_to_drop, inplace=True)

# ---------------------------------------------------------
# 4. Merge All Datasets
# ---------------------------------------------------------
print("Merging datasets...")
# Start merging temp data (European countries only, 2000-2020)
df_merged = pd.merge(df_temp_metrics, df_co2, on=['Country', 'Year'], how='left')
df_merged = pd.merge(df_merged, df_energy, on=['Country', 'Year'], how='left')

# Save to processed directory
output_file = "data/processed/combined_climate_energy.csv"
# Round temperature averages and volatility to the first decimal
df_merged['AnnualMeanTemp'] = df_merged['AnnualMeanTemp'].round(1)
df_merged['TempVolatility'] = df_merged['TempVolatility'].round(1)

df_merged.to_csv(output_file, index=False)
print(f"[OK] Combined climate-energy dataset saved to {output_file} ({len(df_merged)} rows)")

print("=== Data Processing and Integration Completed successfully ===")

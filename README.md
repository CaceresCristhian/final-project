# European Climate & Grid Decarbonization Portfolio
### Summer 2026 Data Visualization Final Project

This repository contains the complete portfolio for the **Data Visualization (Summer 2026) Final Individual Project**. 

It weaves together **regional temperature records and MLP forecasting models** (derived from 1.5 million daily temperature observations) with the **Our World in Data (OWID) Global Energy Transition & CO2 Decoupling** datasets. 

The deliverables are structured in three ways:
1.  **Analysis Notebook (`analysis_notebook.ipynb`):** A pre-rendered Jupyter Notebook containing 10 multi-dimensional analytical questions answered with publication-ready Plotly charts.
2.  **Streamlit Dashboard (`app.py`):** An interactive, multi-tab web application with filters, sliders, metrics, and logistic S-curve mathematical models.
3.  **PDF Slide Deck:** Exportable summaries outlining the results and dashboard screenshots.

---

## 📂 Project Architecture

```
Visualization/
├── data/
│   ├── raw/
│   │   ├── europe_temperatures.csv     # 15MB European temperature dataset (extracted for GitHub size compliance)
│   │   ├── owid-co2-data.csv           # Global emissions data from OWID GitHub
│   │   └── owid-energy-data.csv        # Global energy source shares from OWID GitHub
│   └── processed/
│       └── combined_climate_energy.csv   # Integrated, cleaned annual dataset
├── results/
│   └── europe_forecast_data.json       # Precomputed daily MLP temperature forecasts
├── analysis_notebook.ipynb             # Jupyter Notebook containing the 10 Plotly visualizations
├── app.py                              # Interactive Streamlit dashboard
├── data_pipeline.py                    # ETL script to clean and merge all inputs
├── requirements.txt                    # List of required Python packages
└── README.md                           # Project documentation (this file)
```

---

## ⚖️ Portfolio Design Principles
All charts in this portfolio adhere to strict visual guidelines:
*   **Plotly Only:** No Matplotlib or Seaborn traces.
*   **CVD-Safe Color Palettes:** Using color schemes friendly to color-blind users (Color Brewer theme).
*   **Takeaway Titles:** Every figure title states the clinical or statistical insight, not just a list of variables.
*   **Clean Geometry:** High-contrast white backgrounds, minimal redundant ink, and decluttered gridlines.
*   **Contextual Focus:** Muted grey tones for background/contextual records and a single vibrant color (orange/green) to guide the reader's eye to the main data point.

---

## 📊 The 10 Analytical Questions Explored
The Jupyter Notebook explores these 10 multi-dimensional inquiries:
1.  **Regional Temperature Anomalies:** Geographical choropleth tracking warming trends from 2005 to 2020.
2.  **CO2 Footprint vs. Temperature Volatility:** Scatterplot with marginal distributions comparing cumulative emissions to seasonal variance.
3.  **Economic Carbon Decoupling:** Line charts of Carbon Intensity of GDP (kg CO2/GDP) vs. Year, and Dual-Axis timelines of GDP vs. CO2 over time, showing decoupling dynamics.
4.  **Grid Composition Evolution:** Faceted area chart mapping the transition of coal, gas, nuclear, wind, and solar grids.
5.  **Coal-to-Renewables Displacement:** Dual-axis visualization showing fossil fuel reduction vs. renewable growth and electricity carbon intensity (gCO2/kWh) in Spain.
6.  **Low-Carbon Share vs. Carbon Intensity:** Scatterplot with OLS regression comparing renewable/nuclear mix vs. electricity emissions.
7.  **Spatial GHG Footprint:** Geographic bubble map sizing emissions per-capita across Europe.
8.  **Decadal Temperature Spreads:** Boxplots evaluating summer-winter extremes in Spain over the past two decades.
9.  **Predictability vs. Latitude:** Scatterplot correlating geographic coordinates to MLP forecasting errors (MAE in °C).
10. **Logistic S-Curve Projection:** Logistic regression models ($P(t) = L / (1 + e^{-k(t-t_0)})$) mapping when Spain will achieve an 80% clean energy grid share.

---

## 🚀 Execution & Deployment Instructions

### 1. Installation
Install the necessary dependencies from your terminal:
```bash
pip install -r requirements.txt
```

### 2. Run the Data Pipeline (ETL)
If you need to rebuild the combined dataset, run the pipeline script:
```bash
python data_pipeline.py
```
This script reads the lightweight 15MB European temperature subset, converts Fahrenheit to Celsius, handles outlier sensor values, merges the data with OWID energy/CO2 tables, and saves the output to `data/processed/combined_climate_energy.csv`.

### 3. Launch the Streamlit Dashboard
Run the Streamlit server locally to explore the dashboard:
```bash
streamlit run app.py
```
This opens the interactive app in your default web browser (typically at `http://localhost:8501`).

### 4. Deploying to Streamlit Community Cloud
To share your live dashboard with instructors:
1.  Push the files to a public GitHub repository.
2.  Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3.  Click **"Deploy an app"**, select this repository, specify `app.py` as the main entrypoint, and deploy.

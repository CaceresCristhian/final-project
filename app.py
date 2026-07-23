import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION & CUSTOM STYLE
# ==============================================================================
st.set_page_config(
    page_title="Climate & Energy Transition Portfolio",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling (Glassmorphism & Clean Typography)
st.markdown("""
<style>
    .reportview-container {
        background: #f8f9fa;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eaeaea;
        margin-bottom: 15px;
    }
    h1, h2, h3 {
        font-family: 'Arial', sans-serif;
        color: #2c3e50;
    }
    .highlight-box {
        background: #fff8f2;
        border-left: 5px solid #d95f02;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA LOADERS (Cached for low latency)
# ==============================================================================
@st.cache_data
def load_combined_data():
    df = pd.read_csv('data/processed/combined_climate_energy.csv')
    return df

@st.cache_data
def load_forecast_json():
    with open('results/europe_forecast_data.json', 'r') as f:
        data = json.load(f)
    return data

df = load_combined_data()
forecast_data = load_forecast_json()

# Available countries mapping
countries_list = sorted(list(forecast_data.keys()))

# ==============================================================================
# SIDEBAR CONTROL PANEL
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/000000/earth-globe.png", width=80)
st.sidebar.title("Navigation & Filters")
st.sidebar.markdown("---")

# Global country select
selected_country = st.sidebar.selectbox(
    "Primary Target Country",
    countries_list,
    index=countries_list.index("Spain") if "Spain" in countries_list else 0
)

# Year Range slider
year_range = st.sidebar.slider(
    "Analysis Time Window",
    min_value=2000,
    max_value=2020,
    value=(2000, 2020)
)

st.sidebar.markdown("""
### 📢 Dashboard Features:
*   **Tab 1:** MLP Model Climate Forecasts (Fahrenheit vs. Celsius toggle).
*   **Tab 2:** GDP & Carbon Decoupling trajectories.
*   **Tab 3:** Power Grid Decarbonization & fuel shares.
*   **Tab 4:** European Geographic Choropleth Map.
*   **Tab 5:** Interactive S-Curve projections.
""")

# ==============================================================================
# HEADER HERO SECTION
# ==============================================================================
st.title("🌍 Decarbonization & Climate Dynamics Portfolio")
st.markdown("""
This dashboard details the historical relationships between regional temperature rise, economic growth, and the structural transition of electricity grids across Europe since 2000.
""")

# ==============================================================================
# DASHBOARD TABS
# ==============================================================================
tab_forecast, tab_decoupling, tab_transition, tab_maps, tab_scurve = st.tabs([
    "📈 Daily Climate Forecasts (MLP)",
    "⚖️ Carbon Decoupling (GDP vs CO2)",
    "⚡ Grid Transition Shares",
    "🗺️ Geographic Choropleth Map",
    "🔮 S-Curve Decarbonization Projections"
])

# ------------------------------------------------------------------------------
# TAB 1: Daily Climate Forecasts (MLP)
# ------------------------------------------------------------------------------
with tab_forecast:
    st.subheader(f"Temperature Forecast and Actuals: {selected_country}")
    
    # Retrieve country forecast metadata
    country_meta = forecast_data[selected_country]
    raw_mae = country_meta['mae']
    
    # Unit Toggle
    temp_unit = st.radio("Display Units:", ["Celsius (°C)", "Fahrenheit (°F)"], horizontal=True)
    
    # Conversion calculations
    def convert_val(val, to_unit):
        if val is None:
            return None
        if to_unit == "Celsius (°C)":
            return round((val - 32) * (5/9), 1)
        return round(val, 1)
    
    mae_display = round(raw_mae * (5/9), 1) if temp_unit == "Celsius (°C)" else round(raw_mae, 1)
    unit_str = "°C" if temp_unit == "Celsius (°C)" else "°F"
    
    # Render Metric Cards
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(
            label="Model Prediction Error (MAE)",
            value=f"{mae_display} {unit_str}",
            delta=None
        )
    with col_m2:
        # Calculate mean temperature in 2019
        hist_temps = [d['actual'] for d in country_meta['data'] if d['isHistory']]
        mean_hist = convert_val(np.mean(hist_temps), temp_unit) if hist_temps else 0
        st.metric(
            label="Baseline Mean Temperature (2019)",
            value=f"{mean_hist:.1f} {unit_str}"
        )
    with col_m3:
        # Calculate percentage warming relative to base
        all_actuals = [d['actual'] for d in country_meta['data'] if d['actual'] is not None]
        std_val = convert_val(np.std(all_actuals), temp_unit) if all_actuals else 0
        st.metric(
            label="Historical Temperature Standard Deviation",
            value=f"{std_val:.1f} {unit_str}"
        )
        
    st.markdown("---")
    
    # Build chart data
    plot_rows = []
    for d in country_meta['data']:
        plot_rows.append({
            "date": d['date'],
            "Actual": convert_val(d['actual'], temp_unit),
            "Forecast": convert_val(d['forecast'], temp_unit),
            "isHistory": d['isHistory']
        })
    df_plot = pd.DataFrame(plot_rows)
    df_plot['date'] = pd.to_datetime(df_plot['date'])
    
    # Time Slider to zoom in on specific daily ranges
    min_date = df_plot['date'].min()
    max_date = df_plot['date'].max()
    zoom_dates = st.slider(
        "Forecast Range Filter",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
        format="YYYY-MM-DD"
    )
    
    df_plot_filtered = df_plot[(df_plot['date'] >= zoom_dates[0]) & (df_plot['date'] <= zoom_dates[1])]
    
    fig_f = go.Figure()
    
    # 1. Historical Actuals (2019)
    hist_mask = df_plot_filtered['isHistory']
    fig_f.add_trace(go.Scatter(
        x=df_plot_filtered.loc[hist_mask, 'date'],
        y=df_plot_filtered.loc[hist_mask, 'Actual'],
        name='Historical Daily Mean (2019)',
        line=dict(color='gray', width=1.5),
        opacity=0.6
    ))
    
    # 2. Test Actuals (2020+)
    test_mask = ~df_plot_filtered['isHistory']
    fig_f.add_trace(go.Scatter(
        x=df_plot_filtered.loc[test_mask, 'date'],
        y=df_plot_filtered.loc[test_mask, 'Actual'],
        name='Actual Ground Truth (2020+)',
        line=dict(color='gray', width=1, dash='dash'),
        opacity=0.4
    ))
    
    # 3. Model Predictions (2020+)
    fig_f.add_trace(go.Scatter(
        x=df_plot_filtered.loc[test_mask, 'date'],
        y=df_plot_filtered.loc[test_mask, 'Forecast'],
        name='MLP Model Forecast (2020+)',
        line=dict(color='#d95f02', width=2.5)
    ))
    
    fig_f.update_layout(
        title=f"<b>Daily Temperature Actuals vs. Multi-Layer Perceptron (MLP) Forecast: {selected_country}</b>",
        xaxis_title="Date",
        yaxis_title=f"Temperature ({unit_str})",
        template="plotly_white",
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)')
    )
    st.plotly_chart(fig_f, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: Carbon Decoupling (GDP vs CO2)
# ------------------------------------------------------------------------------
with tab_decoupling:
    st.subheader("⚖️ GDP Growth vs. Per-Capita CO2 Emissions")
    st.markdown("""
    Select multiple countries to compare their GDP per capita and CO2 per capita trajectories. 
    Ideal decoupling trajectories move from right to left (increasing wealth, decreasing emissions).
    """)
    
    decouple_countries = st.multiselect(
        "Compare Countries:",
        list(df['Country'].unique()),
        default=['Germany', 'United Kingdom', 'Spain', 'France']
    )
    
    df_dec = df[
        (df['Country'].isin(decouple_countries)) & 
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1])
    ].sort_values(['Country', 'Year'])
    
    if not df_dec.empty:
        fig_dec = px.line(
            df_dec,
            x='gdp_per_capita',
            y='co2_per_capita',
            color='Country',
            markers=True,
            hover_data=['Year']
        )
        fig_dec.update_layout(
            title="<b>Decoupling Frontier: GDP per Capita vs. CO2 per Capita (2000-2020)</b>",
            xaxis_title="GDP per Capita (USD, PPP adjusted)",
            yaxis_title="CO2 per Capita (Metric Tons)",
            template="plotly_white"
        )
        st.plotly_chart(fig_dec, use_container_width=True)
    else:
        st.warning("Please select at least one country with valid data.")

# ------------------------------------------------------------------------------
# TAB 3: Grid Transition & Fuel Shares
# ------------------------------------------------------------------------------
with tab_transition:
    st.subheader(f"⚡ Power Grid Transition and Carbon Intensity: {selected_country}")
    
    df_trans = df[
        (df['Country'] == selected_country) & 
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1])
    ].sort_values('Year')
    
    if not df_trans.empty:
        # Stacked area chart showing share transition
        df_trans_melted = df_trans.melt(
            id_vars=['Year'], 
            value_vars=['CoalShare', 'GasShare', 'NuclearShare', 'HydroShare', 'SolarShare', 'WindShare'],
            var_name='Source', 
            value_name='Share'
        )
        fig_mix = px.area(
            df_trans_melted,
            x='Year',
            y='Share',
            color='Source',
            color_discrete_sequence=['#4d4d4d', '#e08214', '#b2abd2', '#8073ac', '#fdb863', '#2ca02c']
        )
        fig_mix.update_layout(
            title=f"<b>Electricity Grid Composition Evolution: {selected_country}</b>",
            xaxis_title="Year",
            yaxis_title="Grid Share (%)",
            template="plotly_white"
        )
        st.plotly_chart(fig_mix, use_container_width=True)
        
        # Double-axis displacement check
        fig_dis = go.Figure()
        fig_dis.add_trace(go.Bar(
            x=df_trans['Year'],
            y=df_trans['CoalShare'] + df_trans['GasShare'],
            name='Fossil Fuel share (Coal + Gas) (%)',
            marker_color='#4d4d4d',
            opacity=0.6
        ))
        fig_dis.add_trace(go.Scatter(
            x=df_trans['Year'],
            y=df_trans['WindShare'] + df_trans['SolarShare'],
            name='Solar & Wind Share (%)',
            line=dict(color='#d95f02', width=3)
        ))
        fig_dis.add_trace(go.Scatter(
            x=df_trans['Year'],
            y=df_trans['carbon_intensity_elec'],
            name='Electricity Carbon Intensity (gCO2/kWh)',
            yaxis='y2',
            line=dict(color='#1b9e77', width=3, dash='dash')
        ))
        fig_dis.update_layout(
            yaxis2=dict(
                title='Carbon Intensity (gCO2/kWh)',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            title=f"<b>Fossil Fuel Displacement vs Grid Carbon Intensity: {selected_country}</b>",
            xaxis_title="Year",
            yaxis_title="Grid Share (%)",
            template="plotly_white",
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)')
        )
        st.plotly_chart(fig_dis, use_container_width=True)
        
    else:
        st.warning("No transition data found for this country in the specified range.")

# ------------------------------------------------------------------------------
# TAB 4: Geographic Choropleth Map
# ------------------------------------------------------------------------------
with tab_maps:
    st.subheader("🗺️ Geographic Emissions & Warming Map")
    
    map_year = st.slider("Map Year Select", min_value=2000, max_value=2020, value=2018)
    map_metric = st.selectbox("Map Target Metric:", ["AnnualMeanTemp", "co2", "co2_per_capita", "greenhouse_gas"])
    
    df_map = df[df['Year'] == map_year]
    
    fig_map = px.choropleth(
        df_map,
        locations='iso_code',
        color=map_metric,
        hover_name='Country',
        color_continuous_scale=px.colors.sequential.OrRd if map_metric != "AnnualMeanTemp" else px.colors.diverging.RdYlBu_r,
        scope='europe',
        height=680  # Increase height
    )
    fig_map.update_layout(
        title={
            'text': f"<b>Geographic Distribution of {map_metric} in Europe ({map_year})</b>",
            'y': 0.96,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': '#2c3e50', 'family': 'Arial'}
        },
        margin=dict(l=0, r=0, t=50, b=0),  # Remove margins to utilize full width
        template="plotly_white"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 5: Interactive S-Curve projections
# ------------------------------------------------------------------------------
with tab_scurve:
    st.subheader("🔮 S-Curve Grid Decarbonization Projections")
    st.markdown("""
    Use this interface to model the long-term grid transition. The S-curve represents a logistic diffusion model:
    """)
    st.latex(r"P(t) = \frac{L}{1 + e^{-k(t - t_0)}}")
    
    st.markdown("""
    Where:
    *   **$L$** = Grid capacity saturation limit (100%).
    *   **$k$** = Growth coefficient rate (diffusion speed).
    *   **$t_0$** = Inflection midpoint year (the year of fastest deployment change).
    """)
    
    # Configuration controls
    col_sc1, col_sc2 = st.columns(2)
    with col_sc1:
        param_k = st.slider("Growth Coefficient (k):", min_value=0.05, max_value=0.30, value=0.15, step=0.01)
    with col_sc2:
        param_t0 = st.slider("Inflection Midpoint Year (t0):", min_value=2010, max_value=2035, value=2022)
        
    df_sc = df[df['Country'] == selected_country].sort_values('Year')
    
    if not df_sc.empty:
        proj_years = np.arange(2000, 2045)
        s_curve_vals = 100 / (1 + np.exp(-param_k * (proj_years - param_t0)))
        
        fig_sc = go.Figure()
        
        # Historical Renewables share
        fig_sc.add_trace(go.Scatter(
            x=df_sc['Year'],
            y=df_sc['RenewablesShare'],
            mode='markers+lines',
            name='Historical Renewables Share (%)',
            line=dict(color='#d95f02', width=3)
        ))
        
        # Projections
        fig_sc.add_trace(go.Scatter(
            x=proj_years,
            y=s_curve_vals,
            mode='lines',
            name=f'S-Curve Projection (k={param_k}, t0={param_t0})',
            line=dict(color='#7570b3', width=2, dash='dot')
        ))
        
        fig_sc.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80% Decarbonization Target")
        
        fig_sc.update_layout(
            title=f"<b>Logistic Grid Transition Projection: {selected_country}</b>",
            xaxis_title="Year",
            yaxis_title="Renewable Grid Share (%)",
            template="plotly_white"
        )
        st.plotly_chart(fig_sc, use_container_width=True)
        
        # Project targets
        target_years = proj_years[s_curve_vals >= 80]
        if len(target_years) > 0:
            st.success(f"🎯 Under these parameters, **{selected_country}** is projected to reach the **80% Decarbonization Target** in the year **{target_years[0]}**.")
        else:
            st.warning("The model does not reach 80% grid share within the projected timeline (up to 2045). Try increasing the growth coefficient.")
            
    else:
        st.warning("No data found for S-curve modeling.")

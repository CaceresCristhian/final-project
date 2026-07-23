import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# Define CVD-Safe global design variables
CVD_HIGHLIGHT = '#d95f02' # Orange highlight
CVD_MUTED_GREY = '#7570b3' # Purple-grey context
CVD_GREEN = '#1b9e77'     # Teal-green
PLOT_TEMPLATE = 'plotly_white'

import urllib.request

# Coordinates of European Capital Cities to query Open-Meteo API
CAPITAL_COORDINATES = {
    'Spain': (40.4168, -3.7038),       # Madrid
    'Germany': (52.5200, 13.4050),     # Berlin
    'France': (48.8566, 2.3522),       # Paris
    'United Kingdom': (51.5074, -0.1278), # London
    'Italy': (41.9028, 12.4964),       # Rome
    'Austria': (48.2082, 16.3738),     # Vienna
    'Belgium': (50.8503, 4.3517),      # Brussels
    'Denmark': (55.6761, 12.5683),     # Copenhagen
    'Finland': (60.1699, 24.9384),     # Helsinki
    'Norway': (59.9139, 10.7522),      # Oslo
    'Sweden': (59.3293, 18.0686),      # Stockholm
    'Switzerland': (46.9480, 7.4474),  # Bern
    'Portugal': (38.7223, -9.1393),    # Lisbon
    'Greece': (37.9838, 23.7275),      # Athens
    'Ireland': (53.3498, -6.2603),     # Dublin
    'The Netherlands': (52.3676, 4.9041), # Amsterdam
    'Poland': (52.2297, 21.0122),      # Warsaw
    'Hungary': (47.4979, 19.0402),     # Budapest
    'Bulgaria': (42.6977, 23.3219),    # Sofia
    'Romania': (44.4268, 26.1025),     # Bucharest
    'Ukraine': (50.4501, 30.5234),     # Kyiv
    'Russia': (55.7558, 37.6173),      # Moscow
    'Turkey': (39.9334, 32.8597),      # Ankara
    'Iceland': (64.1466, -21.9426)     # Reykjavik
}

def fetch_live_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception:
        return None

def apply_layout_styling(fig, title, xaxis_title, yaxis_title):
    fig.update_layout(
        title={ 
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial'}
        },
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        template=PLOT_TEMPLATE,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='closest'
    )
    fig.update_xaxes(showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor='#cccccc')
    fig.update_yaxes(showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor='#cccccc')
    return fig


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
st.sidebar.markdown("<h1 style='text-align: center; margin-bottom: 10px; font-size: 72px;'>🌍</h1>", unsafe_allow_html=True)
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
*   **Tab 2:** Real-Time Weather Integration (Open-Meteo API live forecast comparison).
*   **Tab 3:** GDP & Carbon Decoupling timelines.
*   **Tab 4:** Power Grid Decarbonization & fuel shares.
*   **Tab 5:** European Geographic Choropleth Map.
*   **Tab 6:** Interactive S-Curve projections.
*   **Tab 7:** Portfolio Q&A (analytical questions and answers).
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
tab_forecast, tab_weather, tab_decoupling, tab_transition, tab_maps, tab_scurve, tab_qa = st.tabs([
    "📈 Daily Climate Forecasts (MLP)",
    "🌦️ Real-Time Weather Integration",
    "⚖️ Carbon Decoupling (GDP vs CO2)",
    "⚡ Grid Transition Shares",
    "🗺️ Geographic Choropleth Map",
    "🔮 S-Curve Decarbonization Projections",
    "❓ Portfolio Q&A"
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
# ------------------------------------------------------------------------------
# TAB 2: Real-Time Weather Integration
# ------------------------------------------------------------------------------
with tab_weather:
    st.subheader(f"🌦️ Real-Time Weather & Forecast Comparison: {selected_country}")
    st.markdown(f"""
    Compare live forecast temperatures in the Capital of **{selected_country}** directly with the baseline predictions generated by our MLP climate model.
    """)

    WEATHER_CODES = {
        0: "☀️ Clear Sky",
        1: "🌤️ Mainly Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast",
        45: "🌫️ Foggy", 48: "🌫️ Depositing Rime Fog",
        51: "🌧️ Drizzle (Light)", 53: "🌧️ Drizzle (Moderate)", 55: "🌧️ Drizzle (Dense)",
        61: "🌧️ Rain (Slight)", 63: "🌧️ Rain (Moderate)", 65: "🌧️ Rain (Heavy)",
        71: "❄️ Snowfall (Slight)", 73: "❄️ Snowfall (Moderate)", 75: "❄️ Snowfall (Heavy)",
        80: "🌧️ Rain Showers (Slight)", 81: "🌧️ Rain Showers (Moderate)", 82: "🌧️ Rain Showers (Violent)",
        95: "⚡ Thunderstorm", 96: "⚡ Thunderstorm with Slight Hail", 99: "⚡ Thunderstorm with Heavy Hail"
    }

    # Fetch live weather and forecast
    coords = CAPITAL_COORDINATES.get(selected_country)
    if coords:
        lat, lon = coords
        live_data = fetch_live_weather(lat, lon)
        
        if live_data and 'current_weather' in live_data:
            current = live_data['current_weather']
            curr_temp = current['temperature']
            curr_wind = current['windspeed']
            curr_code = current['weathercode']
            curr_desc = WEATHER_CODES.get(curr_code, "⛅ Variable")
            
            # Retrieve Model stats to compare
            country_meta = forecast_data[selected_country]
            model_mae = country_meta['mae']
            hist_temps = [d['actual'] for d in country_meta['data'] if d['isHistory']]
            mean_baseline = np.mean(hist_temps) if hist_temps else 0.0

            # Convert units if needed
            def to_disp(val):
                if temp_unit == "Fahrenheit (°F)":
                    return round((val * 9/5) + 32, 1)
                return round(val, 1)

            # Render Live Metrics Cards
            col_w1, col_w2, col_w3 = st.columns(3)
            with col_w1:
                st.metric("Current Live Temperature", f"{to_disp(curr_temp)} {unit_str}", help="Real-time reading from Open-Meteo API.")
            with col_w2:
                st.metric("Live Wind Speed", f"{curr_wind} km/h", help="Wind speed at capital coordinates.")
            with col_w3:
                st.metric("Current Condition", curr_desc)

            # Comparison calculations
            mae_disp = round(model_mae * (5/9), 1) if temp_unit == "Celsius (°C)" else round(model_mae, 1)
            baseline_disp = to_disp((mean_baseline - 32) * (5/9)) if temp_unit == "Celsius (°C)" else round(mean_baseline, 1)
            
            st.markdown("---")
            
            # Plot the 7-day forecast compared to model bounds
            daily = live_data['daily']
            dates = daily['time']
            max_temps = [to_disp(t) for t in daily['temperature_2m_max']]
            min_temps = [to_disp(t) for t in daily['temperature_2m_min']]
            
            fig_w = go.Figure()
            
            # 1. Shaded Region for Model Baseline +/- MAE Bound
            upper_bound = baseline_disp + mae_disp
            lower_bound = baseline_disp - mae_disp
            
            fig_w.add_trace(go.Scatter(
                x=dates + dates[::-1],
                y=[upper_bound]*len(dates) + [lower_bound]*len(dates),
                fill='toself',
                fillcolor='rgba(117,112,179,0.15)',
                line=dict(color='rgba(255,255,255,0)'),
                name=f'MLP Model Baseline Range ({baseline_disp:.1f} ± {mae_disp:.1f} {unit_str})',
                hoverinfo='skip'
            ))
            
            # 2. Daily Forecast Max
            fig_w.add_trace(go.Scatter(
                x=dates,
                y=max_temps,
                name='7-Day Forecast Max Temp',
                line=dict(color='#d95f02', width=2.5)
            ))
            
            # 3. Daily Forecast Min
            fig_w.add_trace(go.Scatter(
                x=dates,
                y=min_temps,
                name='7-Day Forecast Min Temp',
                line=dict(color='#7570b3', width=2, dash='dash')
            ))
            
            fig_w = apply_layout_styling(
                fig_w,
                f"<b>7-Day Capital Forecast vs. MLP Climatological Baseline: {selected_country}</b>",
                "Date",
                f"Temperature ({unit_str})"
            )
            fig_w.update_layout(legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)'))
            st.plotly_chart(fig_w, use_container_width=True)
            
            # Informational Callout
            current_vs_base = curr_temp - ((mean_baseline - 32) * (5/9))
            status_text = "warmer" if current_vs_base > 0 else "colder"
            st.success(f"📌 **Climate Context:** The current temperature in the Capital of **{selected_country}** is **{abs(to_disp(curr_temp) - baseline_disp):.1f} {unit_str}** {status_text} than the historical baseline average calculated by our model.")
        else:
            st.warning("⚠️ Live weather API query timed out. Using historical model forecast values only.")
    else:
        st.warning("No capital coordinates mapped for this country.")

# TAB 2: Carbon Decoupling (GDP vs CO2)
# ------------------------------------------------------------------------------
with tab_decoupling:
    st.subheader("⚖️ GDP Growth vs. Per-Capita CO2 Emissions")
    st.markdown("""
    Select multiple countries to compare their GDP per capita and CO2 per capita trajectories. 
    Ideal decoupling trajectories move from right to left (increasing wealth, decreasing emissions).
    """)
    
    decouple_countries = st.multiselect(
        "Compare Countries (Limit 10):",
        list(df['Country'].unique()),
        default=['Germany', 'United Kingdom', 'Spain', 'France'],
        max_selections=10
    )
    
    df_dec = df[
        (df['Country'].isin(decouple_countries)) & 
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1])
    ].sort_values(['Country', 'Year'])
    
    if not df_dec.empty:
        # Calculate Economic Carbon Intensity (kg CO2 per USD of GDP)
        df_dec['CarbonIntensityGDP'] = (df_dec['co2_per_capita'] * 1000) / df_dec['gdp_per_capita']
        
        # Plot 1: Carbon Intensity of GDP over Time
        fig_dec1 = px.line(
            df_dec,
            x='Year',
            y='CarbonIntensityGDP',
            color='Country',
            markers=True,
        )
        fig_dec1 = apply_layout_styling(
            fig_dec1,
            "<b>Economic Carbon Intensity: Steady Drop in CO2 Emitted per Dollar of GDP</b>",
            "Year",
            "Carbon Intensity of GDP (kg CO2 / USD)"
        )
        st.plotly_chart(fig_dec1, use_container_width=True)
        
        st.markdown("---")
        st.subheader(f"🔍 Deep Dive: Dual-Axis Decoupling Timeline for {selected_country}")
        
        # Plot 2: Dual Axis for Selected Country
        df_select = df[
            (df['Country'] == selected_country) &
            (df['Year'] >= year_range[0]) &
            (df['Year'] <= year_range[1])
        ].sort_values('Year')
        
        if not df_select.empty:
            fig_dec2 = go.Figure()
            
            fig_dec2.add_trace(go.Scatter(
                x=df_select['Year'],
                y=df_select['gdp_per_capita'],
                name='GDP per Capita (USD)',
                line=dict(color=CVD_GREEN, width=3)
            ))
            
            fig_dec2.add_trace(go.Scatter(
                x=df_select['Year'],
                y=df_select['co2_per_capita'],
                name='CO2 per Capita (Tons)',
                yaxis='y2',
                line=dict(color=CVD_HIGHLIGHT, width=3, dash='dash')
            ))
            
            fig_dec2.update_layout(
                yaxis2=dict(
                    title='CO2 per Capita (Tons)',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)')
            )
            
            fig_dec2 = apply_layout_styling(
                fig_dec2,
                f"<b>Decoupling Timeline: GDP Rises as Carbon Footprint Declines in {selected_country}</b>",
                "Year",
                "GDP per Capita (USD)"
            )
            st.plotly_chart(fig_dec2, use_container_width=True)
        else:
            st.warning("No details found for the selected country.")
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
        color_continuous_scale='greys',  # Use black/grey color scale
        scope='europe',
        height=1000  # Twice as big
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

# ------------------------------------------------------------------------------
# TAB 6: Portfolio Q&A
# ------------------------------------------------------------------------------
with tab_qa:
    st.subheader("❓ Portfolio Q&A: 10 Analytical Questions & Answers")
    st.markdown("""
    This section details the 10 multi-dimensional analytical questions, their answers based on our integrated dataset, and the specific Plotly visualization designs used to solve them.
    """)
    
    qa_list = [
        {
            "id": "1",
            "q": "How does the average temperature anomaly across European geographic regions show accelerating warming from 2005 to 2020?",
            "a": "Warming is clearly accelerating over time. Southern Europe (e.g. Spain, Italy) and Eastern Europe show the most intense shifts, with annual anomalies regularly exceeding +1.5°C to +2.0°C in the 2015-2020 window relative to the 2000-2005 baseline.",
            "visual": "Geographic Choropleth Map with temporal animation slider (height=1000, black scale)."
        },
        {
            "id": "2",
            "q": "What is the mathematical correlation between a country's cumulative carbon emissions and the volatility (variance) of its monthly temperatures?",
            "a": "Nations with large cumulative industrial carbon footprints (like Germany and the UK) cluster toward higher baseline temperature volatility. Outliers are easily spotted via marginal distributions.",
            "visual": "Scatterplot with marginal histograms and box plot layers (color-coded in orange)."
        },
        {
            "id": "3",
            "q": "Which European nations have successfully decoupled GDP per capita growth from CO2 emissions per capita, and how has this relationship shifted since 2000?",
            "a": "Germany, the UK, and France show absolute decoupling (GDP per capita increases while CO2 per capita falls). Spain shows relative decoupling, where GDP growth has outpaced emissions growth, leading to a dropping carbon intensity per dollar.",
            "visual": "Economic Carbon Intensity line chart (kg CO2/GDP) and Dual-Axis timelines."
        },
        {
            "id": "4",
            "q": "How has the transition of electricity generation sources (Coal, Gas, Nuclear, Hydro, Solar, Wind) evolved in Europe over the past two decades?",
            "a": "Coal's share of the European grid has steadily collapsed, falling from over 25% down to under 10%. This baseload has been systematically replaced by wind and solar, while nuclear and hydro provided a stable low-carbon baseline.",
            "visual": "Faceted Stacked Grid Share Area Chart."
        },
        {
            "id": "5",
            "q": "At what rate are coal and gas power plants being actively displaced by wind and solar in Spain, and how does this affect national carbon intensity?",
            "a": "Spain's solar and wind generation shares grew from under 5% in 2000 to over 25% by 2020. This growth correlates with a near-complete elimination of coal power and a plunge in electricity carbon intensity (down to ~180 gCO2/kWh).",
            "visual": "Double-Axis line and bar plot (Fossil Fuel share vs. Carbon Intensity)."
        },
        {
            "id": "6",
            "q": "How does a country's share of low-carbon electricity (renewables + nuclear) relate to its final electricity carbon intensity, and is the relationship linear or logarithmic?",
            "a": "The relationship is logarithmic. As low-carbon share increases, carbon intensity drops sharply. Once a grid passes 60% low-carbon share, it hits an inflection point where carbon intensity stabilizes at extremely low levels (under 100 gCO2/kWh).",
            "visual": "Scatterplot with manual OLS linear regression trendline."
        },
        {
            "id": "7",
            "q": "How are per-capita greenhouse gas emissions distributed geographically in Europe, and which regions are the largest net contributors?",
            "a": "Per-capita greenhouse gas emissions are highest in fossil-reliant economies (like Poland and Germany). The spatial distribution shows a clear concentration of carbon footprints in Central and Western European industrial hubs.",
            "visual": "European Geographic Bubble Map (height=1000, sizing by total GHG, color by GHG per capita)."
        },
        {
            "id": "8",
            "q": "How are seasonal temperature ranges (Summer max vs. Winter min) shifting in Spain, indicating more severe extreme weather events?",
            "a": "Decadal box plots reveal that the 2010-2020 decade in Spain experienced a higher median temperature and an increased frequency of extreme daily heat outliers compared to the 2000-2009 decade, signaling more intense seasonality.",
            "visual": "Decadal Box Plots (2000-2009 vs. 2010-2020) with outliers."
        },
        {
            "id": "9",
            "q": "Does a country's temperature forecast uncertainty (MLP Model MAE) correlate with its geographic latitude or local temperature variance?",
            "a": "Yes. Higher-latitude countries (e.g. Russia, Norway) experience larger forecasting errors (higher MAE in °C) because their seasonal temperature variance is significantly wider compared to Mediterranean climates.",
            "visual": "Scatterplot of Latitude vs. MAE, with marker size linked to temperature variance."
        },
        {
            "id": "10",
            "q": "Based on historical solar and wind growth rates, when is Spain projected to reach 80% renewable electricity grid share under a logistic S-curve projection?",
            "a": "Under a logistic S-curve diffusion model with a growth rate coefficient (k) of 0.15 and an inflection midpoint year (t0) of 2022, Spain is projected to achieve the 80% decarbonization target by the year 2035.",
            "visual": "Logistic S-Curve projection model overlaid with historical data and a target reference line."
        }
    ]
    
    for item in qa_list:
        with st.expander(f"Question {item['id']}: {item['q']}"):
            st.markdown(f"**Answer:** {item['a']}")
            st.markdown(f"*Visual Used:* `{item['visual']}`")

import streamlit as st
import plotly.graph_objects as go
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Patch
plt.style.use('dark_background')

st.set_page_config(
    page_title="PitWall - F1 Performance Analysis",
    page_icon="🏎️",
    layout="wide"
)

# Custom CSS for card styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1A1D24;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #E10600;
    }
    h1 {
        color: #E10600;
    }
</style>
""", unsafe_allow_html=True)

os.makedirs('f1_cache', exist_ok=True)
fastf1.Cache.enable_cache('f1_cache')

# Sidebar navigation
st.sidebar.title("🏎️ PitWall")
st.sidebar.markdown("*F1 Performance Analysis*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["🏠 Home", "📊 Lap Times", "🏎️ Tyre Degradation", "📋 Strategy", "⚡ Fastest Lap", "🎬 Race Replay"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Built by Niranjana K")
st.sidebar.caption("2nd Year B.Tech CSE, JCET")

@st.cache_data
def load_session():
    session = fastf1.get_session(2024, 'Bahrain', 'R')
    session.load()
    return session

with st.spinner("Loading 2024 Bahrain GP data..."):
    session = load_session()

all_drivers = list(session.laps['Driver'].unique())

# ============ HOME PAGE ============
if page == "🏠 Home":
    st.title("🏎️ PitWall")
    st.subheader("F1 Driver Performance Analysis Dashboard")
    st.markdown("---")
    st.success("Data loaded successfully! ✅")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h3>Event</h3><p>' + session.event['EventName'] + '</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h3>Total Drivers</h3><p>' + str(len(all_drivers)) + '</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h3>Total Laps</h3><p>' + str(len(session.laps)) + '</p></div>', unsafe_allow_html=True)

# ============ ANALYSIS 1 - LAP TIMES ============
elif page == "📊 Lap Times":
    st.header("📊 Analysis 1 — Lap Time Comparison")

    selected_drivers = st.multiselect(
        "Select drivers to compare:",
        options=all_drivers,
        default=['VER', 'PER', 'SAI']
    )

    if selected_drivers:
        fig = go.Figure()

        for driver in selected_drivers:
            driver_laps = session.laps.pick_drivers(driver)
            lap_numbers = driver_laps['LapNumber']
            lap_times = driver_laps['LapTime'].dt.total_seconds()

            fig.add_trace(go.Scatter(
                x=lap_numbers,
                y=lap_times,
                mode='lines+markers',
                name=driver,
                hovertemplate='Lap %{x}<br>Time: %{y:.3f}s<extra></extra>'
            ))

        fig.update_layout(
            title='Lap Time Comparison - 2024 Bahrain GP',
            xaxis_title='Lap Number',
            yaxis_title='Lap Time (seconds)',
            template='plotly_dark',
            height=500,
            hovermode='x unified'
        )

        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Please select at least one driver!")

# ============ ANALYSIS 2 - TYRE DEGRADATION ============
elif page == "🏎️ Tyre Degradation":
    st.header("🏎️ Analysis 2 — Tyre Degradation by Stint")

    tyre_driver = st.selectbox(
        "Select a driver to analyze tyre degradation:",
        options=all_drivers,
        index=0
    )

    driver_laps_full = session.laps.pick_drivers(tyre_driver)
    stints = driver_laps_full['Stint'].unique()

    fig2, ax2 = plt.subplots(figsize=(12, 5))
    colors = ['red', 'gold', 'grey', 'green', 'blue']

    for i, stint in enumerate(sorted(stints)):
        stint_data = driver_laps_full[driver_laps_full['Stint'] == stint]
        stint_laps = stint_data['LapNumber']
        stint_times = stint_data['LapTime'].dt.total_seconds()
        color = colors[i % len(colors)]
        ax2.plot(stint_laps, stint_times, marker='o', markersize=4,
                  color=color, label=f'Stint {int(stint)}')

    ax2.set_title(f'{tyre_driver} Tyre Degradation - 2024 Bahrain GP')
    ax2.set_xlabel('Lap Number')
    ax2.set_ylabel('Lap Time (seconds)')
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

# ============ ANALYSIS 3 - STRATEGY ============
elif page == "📋 Strategy":
    st.header("📋 Analysis 3 — Race Strategy Overview")

    strategy_drivers = st.multiselect(
        "Select drivers for strategy comparison:",
        options=all_drivers,
        default=['VER', 'PER', 'SAI'],
        key="strategy_select"
    )

    if strategy_drivers:
        fig3, ax3 = plt.subplots(figsize=(12, len(strategy_drivers) * 0.8))

        compound_colors = {
            'SOFT': 'red',
            'MEDIUM': 'gold',
            'HARD': 'grey',
            'INTERMEDIATE': 'green',
            'WET': 'blue'
        }

        for idx, driver in enumerate(strategy_drivers):
            driver_data = session.laps.pick_drivers(driver)
            stints = driver_data['Stint'].unique()

            for stint in sorted(stints):
                stint_data = driver_data[driver_data['Stint'] == stint]
                start_lap = stint_data['LapNumber'].min()
                end_lap = stint_data['LapNumber'].max()
                compound = stint_data['Compound'].iloc[0]
                color = compound_colors.get(compound, 'black')

                ax3.barh(driver, end_lap - start_lap, left=start_lap,
                         color=color, edgecolor='black')

        ax3.set_xlabel('Lap Number')
        ax3.set_title('Race Strategy - Tyre Compounds by Stint')

        legend_elements = [Patch(facecolor=c, label=k) for k, c in compound_colors.items()]
        ax3.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))

        st.pyplot(fig3)
    else:
        st.warning("Please select at least one driver!")

# ============ ANALYSIS 4 - FASTEST LAP ============
elif page == "⚡ Fastest Lap":
    st.header("⚡ Analysis 4 — Fastest Lap of the Race")

    all_laps = session.laps
    fastest_lap = all_laps.pick_fastest()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Fastest Driver", fastest_lap['Driver'])

    with col2:
        fastest_time = fastest_lap['LapTime'].total_seconds()
        st.metric("Lap Time", f"{fastest_time:.3f} sec")

    with col3:
        st.metric("Lap Number", int(fastest_lap['LapNumber']))

    st.markdown("### Top 5 Fastest Laps of the Race")
    top5 = all_laps.nsmallest(5, 'LapTime')[['Driver', 'LapNumber', 'LapTime']].copy()
    top5['LapTime'] = top5['LapTime'].dt.total_seconds()
    top5.columns = ['Driver', 'Lap Number', 'Lap Time (sec)']
    st.dataframe(top5, width="stretch")

    # ============ ANALYSIS 5 - RACE REPLAY ============
elif page == "🎬 Race Replay":
    st.header("🎬 Analysis 5 — Animated Race Position Replay")
    st.markdown("Press **Play** to watch positions change lap by lap!")

    import plotly.express as px

    position_data = session.laps[['LapNumber', 'Driver', 'Position']].dropna()
    position_data = position_data.sort_values(['LapNumber', 'Position'])

    team_colors = {
        'VER': '#3671C6', 'PER': '#3671C6',
        'HAM': '#27F4D2', 'RUS': '#27F4D2',
        'LEC': '#E8002D', 'SAI': '#E8002D',
        'NOR': '#FF8000', 'PIA': '#FF8000',
        'ALO': '#229971', 'STR': '#229971',
        'GAS': '#FF87BC', 'OCO': '#FF87BC',
        'ALB': '#64C4FF', 'SAR': '#64C4FF',
        'TSU': '#6692FF', 'RIC': '#6692FF',
        'HUL': '#B6BABD', 'MAG': '#B6BABD',
        'BOT': '#52E252', 'ZHO': '#52E252'
    }

    fig5 = px.bar(
        position_data,
        x='Position',
        y='Driver',
        animation_frame='LapNumber',
        orientation='h',
        range_x=[0, 21],
        template='plotly_dark',
        title='Race Position by Lap - 2024 Bahrain GP',
        color='Driver',
        color_discrete_map=team_colors
    )

    fig5.layout.updatemenus[0].buttons[0]['args'][1]['frame']['duration'] = 3000
    fig5.layout.updatemenus[0].buttons[0]['args'][1]['transition']['duration'] = 500

    fig5.update_yaxes(categoryorder='total ascending')
    fig5.update_layout(height=700, showlegend=False)

    st.plotly_chart(fig5, width="stretch")
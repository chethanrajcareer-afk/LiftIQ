import streamlit as st
import plotly.express as px

from analytics.experiment import generate_workload, run_experiment

# --------------------------------------------------
# PAGE CONFIGURATION
# Must be the first Streamlit command in this file.
# --------------------------------------------------

st.set_page_config(
    page_title="LiftIQ | Elevator Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }

    .liftiq-wordmark {
        font-family: 'Barlow Condensed', 'Arial Narrow', sans-serif !important;
        font-size: 64px;
        line-height: 0.95;
        font-weight: 900;
        letter-spacing: 1.5px;
        color: #C9A65B;
        margin: 0;
        text-transform: uppercase;
    }

    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #DDE3EC;
    }

    [data-testid="stSidebar"] h2 {
        font-family: 'Barlow Condensed', 'Arial Narrow', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
    }

    .stApp {
        background-color: #F1F5F9;
        color: #0B1F3A;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #0B1F3A !important;
        font-weight: 800 !important;
    }

    h1 {
        font-size: 40px !important;
    }

    h2 {
        font-size: 28px !important;
    }

    h3 {
        font-size: 22px !important;
    }

    p, label, [data-testid="stCaptionContainer"] {
        color: #334155;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DDE3EC;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 2px 5px rgba(11, 31, 58, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: #0B1F3A !important;
        font-weight: 800 !important;
    }

    div.stButton > button {
        background: #059669;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: 700;
    }

    div.stButton > button:hover {
        background: #047857;
        color: #FFFFFF;
    }

    hr {
        border-color: #DDE3EC;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# REUSABLE PLOTLY CHART THEME
# --------------------------------------------------


def style_chart(fig):
    """Apply LiftIQ's light chart theme and readable typography."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#F1F5F9",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Inter, Segoe UI, sans-serif",
            color="#0B1F3A",
            size=14,
        ),
        title=dict(
            font=dict(
                size=23,
                color="#0B1F3A",
                family="Inter, Segoe UI, sans-serif",
            ),
            x=0.02,
            xanchor="left",
        ),
        xaxis=dict(
            title_font=dict(size=16, color="#0B1F3A"),
            tickfont=dict(size=14, color="#334155"),
            gridcolor="#E2E8F0",
            linecolor="#CBD5E1",
            zerolinecolor="#CBD5E1",
        ),
        yaxis=dict(
            title_font=dict(size=16, color="#0B1F3A"),
            tickfont=dict(size=14, color="#334155"),
            gridcolor="#E2E8F0",
            linecolor="#CBD5E1",
            zerolinecolor="#CBD5E1",
        ),
        margin=dict(l=55, r=25, t=85, b=60),
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(size=14, color="#0B1F3A"),
    )
    return fig


# --------------------------------------------------
# HEADER
# --------------------------------------------------

header_col, status_col = st.columns([5.5, 1.5], vertical_alignment="center")

with header_col:
    st.markdown(
        """
        <div class="liftiq-wordmark">LIFTIQ</div>
        <p style="color:#475569; font-size:16px; font-weight:600; margin-top:8px;">
            CHRIST UNIVERSITY | ELEVATOR INTELLIGENCE PLATFORM
        </p>
        """,
        unsafe_allow_html=True,
    )

with status_col:
    st.markdown("### SYSTEM")
    st.success("Simulation Ready")

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

# Keep the CHRIST logo in the sidebar only.
st.sidebar.image("assets/logo.png", width=500)
st.sidebar.markdown(
    "<div style='font-family:Inter,sans-serif; color:#64748B; "
    "font-size:12px; font-weight:700; letter-spacing:1.2px;'>CONTROL CENTRE</div>",
    unsafe_allow_html=True,
)
st.sidebar.divider()
st.sidebar.subheader("Simulation Settings")

passenger_count = st.sidebar.slider(
    "Passenger Requests",
    min_value=10,
    max_value=200,
    value=50,
    step=10,
)

duration = st.sidebar.slider(
    "Simulation Duration",
    min_value=60,
    max_value=600,
    value=120,
    step=30,
)

seed = st.sidebar.number_input(
    "Random Seed",
    min_value=1,
    max_value=10000,
    value=42,
)

st.sidebar.divider()
run_button = st.sidebar.button(
    "RUN SIMULATION", type="primary", use_container_width=True
)
st.sidebar.caption("LiftIQ v0.1 | Academic Prototype")


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "results" not in st.session_state:
    st.session_state.results = None

if "simulation_config" not in st.session_state:
    st.session_state.simulation_config = None


# --------------------------------------------------
# RUN SIMULATION
# --------------------------------------------------

if run_button:
    try:
        with st.spinner("Running elevator simulations..."):
            requests = generate_workload(
                passenger_count=passenger_count,
                seed=int(seed),
                duration=duration,
            )
            results = run_experiment(requests)

            st.session_state.results = results
            st.session_state.simulation_config = {
                "passengers": passenger_count,
                "duration": duration,
                "seed": int(seed),
            }

        st.success("Simulation completed successfully!")

    except Exception as exc:
        st.error(f"The simulation could not be completed: {exc}")
        st.stop()


# --------------------------------------------------
# DASHBOARD EMPTY STATE
# --------------------------------------------------

if st.session_state.results is None:
    st.info(
        "Configure your simulation in the sidebar and click RUN SIMULATION to begin."
    )

    st.markdown("### Platform Overview")
    overview_col1, overview_col2, overview_col3 = st.columns(3)

    overview_col1.metric("Elevators", "6")
    overview_col2.metric("Scheduling Algorithms", "3")
    overview_col3.metric("Simulation Mode", "Synthetic")

    st.stop()


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

results = st.session_state.results
config = st.session_state.simulation_config

if not results:
    st.warning("The experiment returned no results. Please run the simulation again.")
    st.stop()


# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

best_algorithm = min(
    results,
    key=lambda name: results[name]["average_waiting_time"],
)

best_wait = results[best_algorithm]["average_waiting_time"]
total_passengers = results[best_algorithm]["total_passengers"]
completed = results[best_algorithm]["completed_passengers"]
completion_rate = (completed / total_passengers * 100) if total_passengers > 0 else 0
best_p95 = min(metrics["waiting_time_p95"] for metrics in results.values())


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.subheader("Performance Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Passengers", total_passengers)
kpi2.metric("Completed Journeys", completed)
kpi3.metric("Completion Rate", f"{completion_rate:.1f}%")
kpi4.metric("Best Average Wait", f"{best_wait:.2f}")

st.caption(f"Best average waiting time: {best_algorithm}")
st.divider()


# --------------------------------------------------
# ALGORITHM COMPARISON
# --------------------------------------------------

st.subheader("Scheduling Algorithm Intelligence")

algorithm_names = list(results.keys())

avg_wait_data = [
    {
        "Algorithm": name,
        "Average Waiting Time": results[name]["average_waiting_time"],
    }
    for name in algorithm_names
]

p95_data = [
    {
        "Algorithm": name,
        "95th Percentile Waiting": results[name]["waiting_time_p95"],
    }
    for name in algorithm_names
]

chart_left, chart_right = st.columns(2)

with chart_left:
    fig_avg = px.bar(
        avg_wait_data,
        x="Algorithm",
        y="Average Waiting Time",
        title="Average Passenger Waiting Time",
        text_auto=".2f",
        color_discrete_sequence=["#264796"],
    )
    fig_avg.update_yaxes(title_text="Average Waiting Time (simulation units)")
    fig_avg = style_chart(fig_avg)
    st.plotly_chart(fig_avg, use_container_width=True)

with chart_right:
    fig_p95 = px.bar(
        p95_data,
        x="Algorithm",
        y="95th Percentile Waiting",
        title="Passenger Waiting Time Distribution",
        text_auto=".2f",
        color_discrete_sequence=["#264796"],
    )
    fig_p95.update_yaxes(title_text="95th Percentile Waiting Time (simulation units)")
    fig_p95 = style_chart(fig_p95)
    st.plotly_chart(fig_p95, use_container_width=True)

st.divider()


# --------------------------------------------------
# ELEVATOR UTILISATION
# --------------------------------------------------

st.subheader("Elevator Fleet Intelligence")

selected_algorithm = st.selectbox(
    "Select Scheduling Algorithm",
    algorithm_names,
)

elevator_data = results[selected_algorithm]["elevator_utilisation"]

utilisation_data = []
for elevator_id, metrics in elevator_data.items():
    utilisation_data.append(
        {
            "Elevator": elevator_id,
            "Utilisation": metrics["utilisation_percentage"],
            "Busy Time": metrics["busy_time"],
            "Idle Time": metrics["idle_time"],
        }
    )

fig_util = px.bar(
    utilisation_data,
    x="Elevator",
    y="Utilisation",
    text="Utilisation",
    title=f"{selected_algorithm} - Elevator Utilisation",
    range_y=[0, 100],
)

fig_util.update_traces(
    marker_color="#C9A65B",
    texttemplate="%{text:.2f}%",
    textposition="outside",
    textfont=dict(
        size=13,
        color="#0B1F3A",
    ),
)

fig_util.update_yaxes(title_text="Elevator Utilisation (%)")

fig_util = style_chart(fig_util)

st.plotly_chart(fig_util, use_container_width=True)


# --------------------------------------------------
# INDIVIDUAL ELEVATOR METRICS
# --------------------------------------------------


st.markdown("### Individual Elevator Status")

elevator_items = list(elevator_data.items())

# Display 3 elevator cards per row
for start in range(0, len(elevator_items), 3):

    elevator_columns = st.columns(3)

    for column, (elevator_id, metrics) in zip(
        elevator_columns, elevator_items[start : start + 3]
    ):
        with column:
            with st.container(border=True):

                column.metric(
                    label=elevator_id, value=f"{metrics['utilisation_percentage']:.2f}%"
                )

                st.caption(f"Busy Time: {metrics['busy_time']:.2f}")

                st.caption(f"Idle Time: {metrics['idle_time']:.2f}")

st.divider()


st.divider()


# --------------------------------------------------
# ANALYTICAL INSIGHTS
# --------------------------------------------------

st.subheader("Performance Insights")

st.markdown(f"""
    **Best average waiting-time algorithm:** {best_algorithm}

    **Lowest average waiting time:** {best_wait:.2f}

    **Best 95th-percentile waiting time:** {best_p95:.2f}

    **Passenger completion rate:** {completion_rate:.1f}%

    **Simulation configuration:**\\
    {config['passengers']} passengers,\\
    {config['duration']} simulation-time units,\\
    random seed {config['seed']}.
    """)


# --------------------------------------------------
# RAW RESULTS
# --------------------------------------------------

with st.expander("View Detailed Algorithm Results"):
    for name, metrics in results.items():
        st.markdown(f"#### {name}")
        st.json(metrics)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "LIFTIQ | Smart Elevator Intelligence | CHRIST University Academic Prototype"
)
st.caption(
    "All displayed results are generated using synthetic simulation data, "
    "not live university lift telemetry."
)

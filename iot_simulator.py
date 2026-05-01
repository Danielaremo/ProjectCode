import streamlit as st
import pandas as pd
import time
import os
from streamlit_autorefresh import st_autorefresh

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="IoT Machine Simulator", layout="wide")

st.title("🟢 IoT Machine Uptime Tracker")

# =========================
# AUTO REFRESH (FIX FOR TIMER)
# =========================
st_autorefresh(interval=500, key="scada_refresh")  # smoother 0.5s refresh

# =========================
# CSV STORAGE
# =========================
CSV_FILE = "session_log.csv"

if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "Session", "Runtime (s)", "Energy (kWh)", "Cost (₦)"
    ])
    df_init.to_csv(CSV_FILE, index=False)

# =========================
# SESSION STATE
# =========================
if "machine_on" not in st.session_state:
    st.session_state.machine_on = False

if "start_time" not in st.session_state:
    st.session_state.start_time = 0

if "sessions" not in st.session_state:
    st.session_state.sessions = []

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.header("Sensor Simulation Controls")

vibration = st.sidebar.slider("Vibration Level", 0, 10, 2)
temperature = st.sidebar.slider("Temperature (°C)", 20, 100, 35)
current = st.sidebar.slider("Current (A)", 0.0, 10.0, 1.0)

tariff = st.sidebar.number_input("Tariff (₦/kWh)", value=62.33)

vib_th = st.sidebar.slider("Vibration Threshold", 0, 10, 3)
temp_th = st.sidebar.slider("Temperature Threshold", 20, 100, 40)
cur_th = st.sidebar.slider("Current Threshold", 0.0, 10.0, 0.5)

# =========================
# ACTIVITY SCORE
# =========================
score = 0
if vibration > vib_th:
    score += 1
if temperature > temp_th:
    score += 1
if current > cur_th:
    score += 1

# =========================
# MACHINE STATE LOGIC
# =========================
if score >= 2:
    if not st.session_state.machine_on:
        st.session_state.start_time = time.time()
    st.session_state.machine_on = True

else:
    if st.session_state.machine_on:
        end_time = time.time()
        runtime = end_time - st.session_state.start_time

        energy = (current * 220 * runtime) / 3600000
        cost = energy * tariff

        session_id = len(st.session_state.sessions) + 1

        st.session_state.sessions.append({
            "Session": session_id,
            "Runtime (s)": runtime,
            "Energy (kWh)": energy,
            "Cost (₦)": cost
        })

        df = pd.DataFrame(st.session_state.sessions)
        df.to_csv(CSV_FILE, index=False)

    st.session_state.machine_on = False

# =========================
# TIME FORMAT FUNCTION
# =========================
def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}"

# =========================
# LIVE UPTIME (FIXED)
# =========================
if st.session_state.machine_on:
    uptime_seconds = time.time() - st.session_state.start_time
else:
    uptime_seconds = 0

uptime_display = format_time(uptime_seconds)

# =========================
# SCADA DISPLAY
# =========================
st.markdown("## MACHINE STATUS")

if st.session_state.machine_on:
    st.markdown("<h2 style='color:lime;'>● RUNNING</h2>", unsafe_allow_html=True)
else:
    st.markdown("<h2 style='color:red;'>● STOPPED</h2>", unsafe_allow_html=True)

# =========================
# BIG UPTIME DISPLAY (FIXED + SCADA STYLE)
# =========================
st.markdown(
    f"""
    <div style='text-align:center; margin-top:10px;'>
        <div style='font-size:20px; color:gray;'>UPTIME</div>
        <div style='font-size:72px; font-weight:bold; color:white;'>
            {uptime_display}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# METRICS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Vibration", vibration)
col2.metric("Temperature (°C)", temperature)
col3.metric("Current (A)", current)

st.markdown("---")

# =========================
# SESSION HISTORY
# =========================
st.subheader("📊 Session History")

df = pd.read_csv(CSV_FILE)
st.dataframe(df, use_container_width=True)

# =========================
# DOWNLOAD CSV
# =========================
with open(CSV_FILE, "rb") as f:
    st.download_button(
        "⬇ Download CSV",
        f,
        file_name="machine_sessions.csv",
        mime="text/csv"
    )

# =========================
# GRAPH
# =========================
st.subheader("📈 Energy & Cost Trends")

if len(df) > 0:
    chart_data = df.set_index("Session")[["Energy (kWh)", "Cost (₦)"]]
    st.line_chart(chart_data)
    

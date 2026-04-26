import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌍 Urban WASH GHG Emissions Tool")

# -------------------------
# GLOBAL FACTORS
# -------------------------
gwp = {"CO2": 1, "CH4": 28, "N2O": 265, "BC": 590}
grid_ef = 0.82
HP_TO_KW = 0.746

# -------------------------
# INPUT SECTION
# -------------------------
with st.expander("📥 Input Parameters", expanded=False):

    st.subheader("🗑️ Solid Waste")
    total_waste = st.number_input("Total Waste (TPD)", 0, 10000, 500)

    st.subheader("🐄 Livestock")
    dairy_count = st.number_input("Dairy Cattle", 0, 1000000, 2000)
    nondairy_count = st.number_input("Non-dairy Cattle", 0, 1000000, 7000)
    young_count = st.number_input("Young Stock", 0, 1000000, 1000)

    EF_DAIRY = 0.1096
    EF_NONDAIRY = 0.0526
    EF_YOUNG = 0.0197

    st.subheader("🗑️ GVP")
    uncollected_pct = st.slider("Uncollected Waste (%)", 0, 100, 20)
    burn_pct = st.slider("Burning (%)", 0, 100, 30)

    EF_CO2 = 1.4
    EF_CH4 = 0.4
    EF_BC = 1.0

    st.subheader("🚽 Septic Tanks")
    septic_population = st.number_input("Population (Septic)", 0, 10000000, 500000)

    BOD = 0.06
    B0 = 0.6
    MCF = 0.5

    st.subheader("🌊 Open Drains")
    drain_population = st.number_input("Population (Drains)", 0, 10000000, 300000)
    MCF_DRAIN = 0.2

    st.subheader("🏘️ Water Pumping")
    total_buildings = st.number_input("Total Buildings", 0, 1000000, 16000)

# -------------------------
# BASELINE CALCULATIONS
# -------------------------

# Livestock
dairy_ch4 = dairy_count * EF_DAIRY
nondairy_ch4 = nondairy_count * EF_NONDAIRY
young_ch4 = young_count * EF_YOUNG

total_livestock_ch4 = dairy_ch4 + nondairy_ch4 + young_ch4
livestock_co2e = total_livestock_ch4 * gwp["CH4"]

# GVP
uncollected = total_waste * (uncollected_pct / 100)
burned = uncollected * (burn_pct / 100)
dumped = uncollected - burned

co2 = burned * EF_CO2
ch4 = (burned + dumped) * EF_CH4
bc = burned * EF_BC

gvp_co2e = co2 * gwp["CO2"] + ch4 * gwp["CH4"] + bc * gwp["BC"]

# Septic
septic_ch4 = septic_population * BOD * B0 * MCF
septic_co2e = septic_ch4 * gwp["CH4"]

# Drains
drain_ch4 = drain_population * BOD * B0 * MCF_DRAIN
drain_co2e = drain_ch4 * gwp["CH4"]

# Water pumping
low = total_buildings * 0.1
bungalow = total_buildings * 0.8
other = total_buildings * 0.1

low_elec = low * 1 * HP_TO_KW * 2
bungalow_elec = bungalow * 0.5 * HP_TO_KW * 0.5
other_elec = other * 1 * HP_TO_KW * 0.5

total_elec = low_elec + bungalow_elec + other_elec
water_co2e = total_elec * grid_ef

# -------------------------
# SECTOR-WISE BREAKDOWN
# -------------------------
sw_scope1 = livestock_co2e + gvp_co2e
sw_scope2 = 0
sw_total = sw_scope1

lw_scope1 = septic_co2e + drain_co2e
lw_scope2 = 0
lw_total = lw_scope1

ws_scope1 = 0
ws_scope2 = water_co2e
ws_total = ws_scope2

grand_total = sw_total + lw_total + ws_total

# -------------------------
# SCENARIO: BIOGAS
# -------------------------
st.markdown("### 🔋 Biogas Scenario")

biogas_share = st.slider("Dung to Biogas (%)", 0, 100, 0)

total_dung = (
    dairy_count * 12 +
    nondairy_count * 10 +
    young_count * 5
)

diverted_dung = total_dung * (biogas_share / 100)

BIOGAS_YIELD = 0.035
biogas_volume = diverted_dung * BIOGAS_YIELD

electricity_generated = biogas_volume * 2
plant_use = electricity_generated * 0.10
net_electricity = electricity_generated - plant_use

avoided_ch4 = total_livestock_ch4 * (biogas_share / 100)
avoided_co2e = avoided_ch4 * gwp["CH4"]

electricity_offset = net_electricity * grid_ef

total_reduction = avoided_co2e + electricity_offset
scenario_total = grand_total - total_reduction

# -------------------------
# DASHBOARD
# -------------------------
st.markdown("---")
st.header("📊 Results")

col1, col2 = st.columns(2)
col1.metric("Baseline (kg CO₂e/day)", round(grand_total, 2))
col2.metric("Scenario (kg CO₂e/day)", round(scenario_total, 2))

reduction = grand_total - scenario_total
st.metric("Reduction (kg CO₂e/day)", round(reduction, 2))

# Sector table
st.markdown("### 📊 Sector-wise Emissions")

sector_df = pd.DataFrame({
    "Sector": ["Solid Waste", "Liquid Waste", "Water Supply"],
    "Scope 1": [sw_scope1, lw_scope1, ws_scope1],
    "Scope 2": [sw_scope2, lw_scope2, ws_scope2],
    "Total": [sw_total, lw_total, ws_total]
})

st.dataframe(sector_df, use_container_width=True)

# Insights
st.markdown("### 🧠 Insights")

sw_pct = (sw_total / grand_total * 100) if grand_total else 0
lw_pct = (lw_total / grand_total * 100) if grand_total else 0
ws_pct = (ws_total / grand_total * 100) if grand_total else 0

top_sector = max(
    {"SW": sw_total, "LW": lw_total, "WS": ws_total},
    key=lambda x: {"SW": sw_total, "LW": lw_total, "WS": ws_total}[x]
)

st.info(f"Top contributor: {top_sector}")
st.info(f"SW {round(sw_pct,1)}% | LW {round(lw_pct,1)}% | WS {round(ws_pct,1)}%")
st.success(f"Scenario reduces emissions by {round((reduction/grand_total)*100 if grand_total else 0,1)}%")
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌍 Urban WASH GHG Emissions Dashboard")

# -------------------------
# CONSTANTS
# -------------------------
gwp = {"CO2": 1, "CH4": 28, "N2O": 265, "BC": 590}
grid_ef = 0.82
HP_TO_KW = 0.746

def to_co2e(co2=0, ch4=0, n2o=0, bc=0):
    return co2 + ch4*28 + n2o*265 + bc*590

# -------------------------
# INPUTS
# -------------------------
with st.expander("📥 Inputs", expanded=False):

    st.subheader("Transport")
    vehicles = st.number_input("Vehicles", 0, 1000, 100)
    distance = st.number_input("Distance (km/day)", 0, 200, 50)
    fuel_eff = st.number_input("Fuel (L/km)", 0.0, 1.0, 0.3)
    ev_eff = st.number_input("EV (kWh/km)", 0.0, 5.0, 0.8)

    st.subheader("Solid Waste")
    waste = st.number_input("Waste (TPD)", 0, 10000, 500)
    uncollected = st.slider("Uncollected %", 0, 100, 20)
    burn = st.slider("Burn %", 0, 100, 30)

    st.subheader("Livestock")
    dairy = st.number_input("Dairy", 0, 100000, 2000)
    nondairy = st.number_input("Non-dairy", 0, 100000, 7000)
    young = st.number_input("Young", 0, 100000, 1000)

    st.subheader("Liquid Waste")
    septic_pop = st.number_input("Septic Population", 0, 10000000, 500000)
    drain_vol = st.number_input("Drain Volume", 0, 100000, 1000)
    bod = st.number_input("BOD", 0.0, 10000.0, 5000.0)
    n_load = st.number_input("Nitrogen Load", 0.0, 10000.0, 1000.0)

    st.subheader("Water")
    ws_vehicles = st.number_input("Water Vehicles", 0, 1000, 50)
    ws_distance = st.number_input("WS Distance", 0, 200, 40)
    buildings = st.number_input("Buildings", 0, 1000000, 16000)

    st.subheader("🔄 Scenario")
    ev_eff_s = st.number_input("Scenario EV Efficiency", 0.0, 5.0, ev_eff)
    burn_s = st.slider("Scenario Burn %", 0, 100, burn)
    building_eff = st.slider("Building Efficiency %", 0, 100, 20)

# -------------------------
# SOLID WASTE
# -------------------------
transport_sw = vehicles * distance * fuel_eff * 2.68

livestock = to_co2e(ch4=(dairy*0.1096 + nondairy*0.0526 + young*0.0197))

uncol = waste*(uncollected/100)
burned = uncol*(burn/100)

gvp = to_co2e(
    co2=burned*1.4,
    ch4=(burned+(uncol-burned))*0.4,
    bc=burned*1
)

sw_scope1 = transport_sw + livestock + gvp

sw_scope2 = vehicles*distance*ev_eff*grid_ef

sw_total = sw_scope1 + sw_scope2

# -------------------------
# LIQUID WASTE
# -------------------------
septic = to_co2e(ch4=septic_pop*0.06*0.6*0.5)
drain = to_co2e(ch4=drain_vol*0.05*0.6*0.2)

treatment = to_co2e(ch4=bod*0.25, n2o=n_load*0.005)

lw_scope1 = septic + drain + transport_sw + treatment
lw_scope2 = vehicles*distance*ev_eff*grid_ef + 5000*grid_ef

lw_total = lw_scope1 + lw_scope2

# -------------------------
# WATER
# -------------------------
ws_scope1 = ws_vehicles * ws_distance * fuel_eff * 2.68

low = buildings*0.1
bung = buildings*0.8
other = buildings*0.1

kwh = (
    low*1*HP_TO_KW*2 +
    bung*0.5*HP_TO_KW*0.5 +
    other*1*HP_TO_KW*0.5
)

ws_scope2 = kwh * grid_ef
ws_total = ws_scope1 + ws_scope2

# -------------------------
# TOTAL
# -------------------------
grand_total = sw_total + lw_total + ws_total

# -------------------------
# DISPLAY
# -------------------------
st.header("🗑️ Solid Waste")
c1,c2 = st.columns(2)
c1.subheader("Scope 1")
c1.metric("Total", round(sw_scope1,2))
c2.subheader("Scope 2")
c2.metric("Total", round(sw_scope2,2))
st.metric("Total SW", round(sw_total,2))

st.header("💧 Liquid Waste")
c1,c2 = st.columns(2)
c1.subheader("Scope 1")
c1.metric("Total", round(lw_scope1,2))
c2.subheader("Scope 2")
c2.metric("Total", round(lw_scope2,2))
st.metric("Total LW", round(lw_total,2))

st.header("🚰 Water")
c1,c2 = st.columns(2)
c1.subheader("Scope 1")
c1.metric("Total", round(ws_scope1,2))
c2.subheader("Scope 2")
c2.metric("Total", round(ws_scope2,2))
st.metric("Total WS", round(ws_total,2))

# -------------------------
# FINAL DASHBOARD
# -------------------------
st.header("🌍 Overall")

df = pd.DataFrame({
    "Sector":["SW","LW","WS"],
    "Scope1":[sw_scope1,lw_scope1,ws_scope1],
    "Scope2":[sw_scope2,lw_scope2,ws_scope2],
    "Total":[sw_total,lw_total,ws_total]
})

st.dataframe(df)

st.plotly_chart(px.bar(df, x="Sector", y=["Scope1","Scope2"], barmode="group"))
st.plotly_chart(px.pie(df, values="Total", names="Sector"))

# -------------------------
# SCENARIO
# -------------------------
burned_s = uncol*(burn_s/100)

gvp_s = to_co2e(
    co2=burned_s*1.4,
    ch4=(burned_s+(uncol-burned_s))*0.4,
    bc=burned_s
)

sw_s = transport_sw + livestock + gvp_s + vehicles*distance*ev_eff_s*grid_ef
ws_s = ws_scope1 + ws_scope2*(1-building_eff/100)

scenario_total = sw_s + lw_total + ws_s

st.header("🔄 Scenario Comparison")

c1,c2 = st.columns(2)
c1.metric("Baseline", round(grand_total,2))
c2.metric("Scenario", round(scenario_total,2))

reduction = grand_total - scenario_total
pct = reduction/grand_total*100 if grand_total else 0

st.metric("Reduction (kg CO2e/day)", round(reduction,2))
st.metric("Reduction %", round(pct,2))

st.plotly_chart(px.bar(
    pd.DataFrame({"Case":["Baseline","Scenario"],"Emissions":[grand_total,scenario_total]}),
    x="Case", y="Emissions"
))
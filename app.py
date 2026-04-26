import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌍 Urban WASH GHG Emissions Dashboard")

# -------------------------
# CONSTANTS
# -------------------------
grid_ef = 0.82
HP_TO_KW = 0.746
gwp = {"CH4": 28, "N2O": 265, "BC": 590}

def to_co2e(co2=0, ch4=0, n2o=0, bc=0):
    return co2 + ch4*28 + n2o*265 + bc*590

# =========================================================
# TABS
# =========================================================
sw_tab, lw_tab, ws_tab = st.tabs(["🗑️ Solid Waste", "💧 Liquid Waste", "🚰 Water Supply"])

# =========================================================
# 🗑️ SOLID WASTE
# =========================================================
with sw_tab:

    st.header("Solid Waste")

    # -------------------------
    # INPUTS
    # -------------------------
    with st.expander("Inputs", expanded=True):

        st.subheader("Transport")
        sw_fossil = st.number_input("Fossil Vehicles", 0, 1000, 80)
        sw_ev = st.number_input("EV Vehicles", 0, 1000, 20)
        sw_dist = st.number_input("Distance (km/day)", 0, 200, 50)
        fuel_eff = st.number_input("Fuel (L/km)", 0.0, 1.0, 0.3)
        ev_eff = st.number_input("EV (kWh/km)", 0.0, 5.0, 0.8)

        st.subheader("GVP")
        waste = st.number_input("Total Waste (TPD)", 0.0, 10000.0, 500.0)
        uncol_pct = st.slider("Uncollected %", 0, 100, 20)
        burn_pct = st.slider("Burn %", 0, 100, 30)

        st.subheader("Processing")
        comp_waste = st.number_input("Compost Waste", 0.0, 10000.0, 72.0)
        inc_waste = st.number_input("Incineration Waste", 0.0, 10000.0, 0.0)
        disp_waste = st.number_input("Disposal Waste", 0.0, 10000.0, 50.0)

        st.subheader("Electricity")
        comp_kwh = st.number_input("Compost kWh", 0, 100000, 1000)
        inc_kwh = st.number_input("Incineration kWh", 0, 100000, 2000)
        mrf_kwh = st.number_input("MRF kWh", 0, 100000, 1500)
        disp_kwh = st.number_input("Disposal kWh", 0, 100000, 1000)

    # -------------------------
    # CALCULATIONS
    # -------------------------
    # Scope 1
    sw_transport_s1 = sw_fossil * sw_dist * fuel_eff * 2.68

    u = waste * (uncol_pct/100)
    b = u * (burn_pct/100)
    d = u - b

    gvp = to_co2e(co2=b*1.4, ch4=d*0.4, bc=b)

    comp = to_co2e(ch4=comp_waste*0.004, n2o=comp_waste*0.0003)
    inc = to_co2e(co2=inc_waste*1.2, ch4=inc_waste*0.0005, n2o=inc_waste*0.0002)
    disp = to_co2e(ch4=disp_waste*0.15*0.5*0.6*0.5)

    sw_scope1 = sw_transport_s1 + gvp + comp + inc + disp

    # Scope 2
    sw_transport_s2 = sw_ev * sw_dist * ev_eff * grid_ef
    sw_elec = (comp_kwh + inc_kwh + mrf_kwh + disp_kwh) * grid_ef

    sw_scope2 = sw_transport_s2 + sw_elec
    sw_total = sw_scope1 + sw_scope2

    # OUTPUT
    st.metric("Scope 1 (kg CO₂e/day)", round(sw_scope1,2))
    st.metric("Scope 2 (kg CO₂e/day)", round(sw_scope2,2))
    st.metric("Total SW", round(sw_total,2))


# =========================================================
# 💧 LIQUID WASTE
# =========================================================
with lw_tab:

    st.header("Liquid Waste")

    with st.expander("Inputs", expanded=True):

        st.subheader("Containment")
        septic_pop = st.number_input("Septic Population", 0, 10000000, 500000)
        drain_len = st.number_input("Drain Length (m)", 0, 100000, 10000)
        drain_area = st.number_input("Drain Area", 0.0, 10.0, 0.5)
        drain_bod = st.number_input("Drain BOD", 0.0, 10.0, 0.05)

        st.subheader("Transport")
        lw_fossil = st.number_input("Fossil Vehicles (LW)", 0, 1000, 50)
        lw_ev = st.number_input("EV Vehicles (LW)", 0, 1000, 10)
        lw_dist = st.number_input("Distance", 0, 200, 40)

        st.subheader("Treatment")
        bod = st.number_input("BOD Load", 0.0, 100000.0, 5000.0)
        n_load = st.number_input("Nitrogen Load", 0.0, 100000.0, 1000.0)

        st.subheader("Electricity")
        lw_kwh = st.number_input("Treatment kWh", 0, 100000, 5000)

    # Scope 1
    septic = to_co2e(ch4=septic_pop * 0.06 * 0.6 * 0.1)
    drain = to_co2e(ch4=drain_len * drain_area * drain_bod * 0.6 * 0.2)

    lw_transport_s1 = lw_fossil * lw_dist * fuel_eff * 2.68
    treatment = to_co2e(ch4=bod*0.6*0.25, n2o=n_load*0.005)

    lw_scope1 = septic + drain + lw_transport_s1 + treatment

    # Scope 2
    lw_transport_s2 = lw_ev * lw_dist * ev_eff * grid_ef
    lw_scope2 = lw_transport_s2 + lw_kwh * grid_ef

    lw_total = lw_scope1 + lw_scope2

    st.metric("Scope 1", round(lw_scope1,2))
    st.metric("Scope 2", round(lw_scope2,2))
    st.metric("Total LW", round(lw_total,2))


# =========================================================
# 🚰 WATER SUPPLY
# =========================================================
with ws_tab:

    st.header("Water Supply")

    with st.expander("Inputs", expanded=True):

        st.subheader("Transport")
        ws_fossil = st.number_input("Fossil Tankers", 0, 1000, 40)
        ws_ev = st.number_input("EV Tankers", 0, 1000, 10)
        ws_dist = st.number_input("Distance", 0, 200, 40)

        st.subheader("Pumping")
        buildings = st.number_input("Total Buildings", 0, 1000000, 16000)

    # Scope 1
    ws_scope1 = ws_fossil * ws_dist * fuel_eff * 2.68

    # Scope 2
    ws_transport_s2 = ws_ev * ws_dist * ev_eff * grid_ef

    low = buildings*0.1
    bung = buildings*0.8
    other = buildings*0.1

    kwh = (
        low*1*HP_TO_KW*2 +
        bung*0.5*HP_TO_KW*0.5 +
        other*1*HP_TO_KW*0.5
    )

    ws_scope2 = ws_transport_s2 + kwh*grid_ef
    ws_total = ws_scope1 + ws_scope2

    st.metric("Scope 1", round(ws_scope1,2))
    st.metric("Scope 2", round(ws_scope2,2))
    st.metric("Total WS", round(ws_total,2))


# =========================================================
# 🌍 FINAL DASHBOARD
# =========================================================
st.header("🌍 Overall Comparison")

df = pd.DataFrame({
    "Sector":["Solid Waste","Liquid Waste","Water Supply"],
    "Scope1":[sw_scope1,lw_scope1,ws_scope1],
    "Scope2":[sw_scope2,lw_scope2,ws_scope2],
    "Total":[sw_total,lw_total,ws_total]
})

st.dataframe(df)

st.plotly_chart(px.bar(df, x="Sector", y=["Scope1","Scope2"], barmode="group"))
st.plotly_chart(px.pie(df, values="Total", names="Sector"))

total = sw_total + lw_total + ws_total
st.metric("Total Emissions (kg CO₂e/day)", round(total,2))

# Insight
top = df.loc[df["Total"].idxmax(),"Sector"]
st.info(f"Highest emitting sector: {top}")
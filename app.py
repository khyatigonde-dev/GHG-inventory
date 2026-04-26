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
B0 = 0.6

def to_co2e(co2=0, ch4=0, n2o=0, bc=0):
    return co2 + ch4*28 + n2o*265 + bc*590

# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3 = st.tabs(["🗑️ Solid Waste", "💧 Liquid Waste", "🚰 Water Supply"])

# =========================================================
# 🗑️ SOLID WASTE
# =========================================================
with tab1:

    st.header("Solid Waste")

    # -------------------------
    # SCOPE 1
    # -------------------------
    with st.expander("Scope 1", expanded=True):

        # Transport
        st.subheader("Transport (Fossil)")
        sw_fossil = st.number_input("Fossil Vehicles (SW)", 0, 1000, 80)
        sw_dist = st.number_input("Distance (km/day)", 0, 200, 50)
        sw_eff = st.number_input("Fuel (L/km)", 0.0, 1.0, 0.3)

        sw_transport_s1 = sw_fossil * sw_dist * sw_eff * 2.68

        # Livestock
        dairy = st.number_input("Dairy", 0, 100000, 2000)
        nondairy = st.number_input("Non-dairy", 0, 100000, 7000)
        young = st.number_input("Young", 0, 100000, 1000)

        livestock = to_co2e(ch4=(dairy*0.1096 + nondairy*0.0526 + young*0.0197))

        # GVP
        st.subheader("GVP")
        waste = st.number_input("Waste (TPD)", 0.0, 10000.0, 130.0)
        uncol = st.slider("Uncollected %", 0, 100, 20)
        burn = st.slider("Burn %", 0, 100, 30)

        u = waste*(uncol/100)
        b = u*(burn/100)
        d = u-b

        gvp = to_co2e(co2=b*1.4, ch4=d*0.4, bc=b)

        # Composting
        comp_w = st.number_input("Compost Waste", 0.0, 10000.0, 72.0)
        comp_em = to_co2e(ch4=comp_w*0.004, n2o=comp_w*0.0003)

        # Incineration
        inc_w = st.number_input("Incineration Waste", 0.0, 10000.0, 0.0)
        inc_em = to_co2e(co2=inc_w*1.2, ch4=inc_w*0.0005, n2o=inc_w*0.0002, bc=inc_w*0.02)

        # Disposal
        disp_w = st.number_input("Disposal Waste", 0.0, 10000.0, 50.0)
        disp_em = to_co2e(ch4=disp_w*0.15*0.5*0.6*0.5)

        sw_scope1 = sw_transport_s1 + livestock + gvp + comp_em + inc_em + disp_em

    # -------------------------
    # SCOPE 2
    # -------------------------
    with st.expander("Scope 2"):

        sw_ev = st.number_input("EV Vehicles (SW)", 0, 1000, 20)
        sw_ev_eff = st.number_input("EV kWh/km", 0.0, 5.0, 0.8)

        transport_s2 = sw_ev * sw_dist * sw_ev_eff * grid_ef

        comp_kwh = st.number_input("Compost kWh", 0, 100000, 1000)
        inc_kwh = st.number_input("Incineration kWh", 0, 100000, 2000)
        mrf_kwh = st.number_input("MRF kWh", 0, 100000, 1500)
        disp_kwh = st.number_input("Disposal kWh", 0, 100000, 1000)

        sw_scope2 = transport_s2 + (comp_kwh+inc_kwh+mrf_kwh+disp_kwh)*grid_ef

    sw_total = sw_scope1 + sw_scope2
    st.metric("Total SW", round(sw_total,2))


# =========================================================
# 💧 LIQUID WASTE
# =========================================================
with tab2:

    st.header("Liquid Waste")

    with st.expander("Scope 1", expanded=True):

        septic_pop = st.number_input("Septic Pop", 0, 10000000, 500000)
        septic = to_co2e(ch4=septic_pop*0.06*B0*0.1)

        drain_len = st.number_input("Drain Length", 0, 100000, 10000)
        drain_area = st.number_input("Drain Area", 0.0, 10.0, 0.5)
        drain = to_co2e(ch4=drain_len*drain_area*0.05*B0*0.2)

        lw_fossil = st.number_input("Fossil Vehicles (LW)", 0, 1000, 50)
        lw_transport = lw_fossil * sw_dist * sw_eff * 2.68

        bod = st.number_input("BOD", 0.0, 100000.0, 5000.0)
        n = st.number_input("Nitrogen", 0.0, 100000.0, 1000.0)

        treatment = to_co2e(ch4=bod*B0*0.25, n2o=n*0.005)

        lw_scope1 = septic + drain + lw_transport + treatment

    with st.expander("Scope 2"):

        lw_ev = st.number_input("EV Vehicles (LW)", 0, 1000, 10)
        lw_ev_eff = st.number_input("EV kWh/km (LW)", 0.0, 5.0, 0.8)

        transport = lw_ev * sw_dist * lw_ev_eff * grid_ef

        lw_kwh = st.number_input("Treatment kWh", 0, 100000, 5000)

        lw_scope2 = transport + lw_kwh*grid_ef

    lw_total = lw_scope1 + lw_scope2
    st.metric("Total LW", round(lw_total,2))


# =========================================================
# 🚰 WATER SUPPLY
# =========================================================
with tab3:

    st.header("Water Supply")

    with st.expander("Scope 1", expanded=True):

        ws_fossil = st.number_input("Fossil Tankers", 0, 1000, 40)
        ws_scope1 = ws_fossil * sw_dist * sw_eff * 2.68

    with st.expander("Scope 2"):

        ws_ev = st.number_input("EV Tankers", 0, 1000, 10)
        ws_ev_eff = st.number_input("EV kWh/km", 0.0, 5.0, 0.8)

        transport = ws_ev * sw_dist * ws_ev_eff * grid_ef

        buildings = st.number_input("Buildings", 0, 1000000, 16000)

        low = buildings*0.1
        bung = buildings*0.8
        other = buildings*0.1

        kwh = (
            low*1*HP_TO_KW*2 +
            bung*0.5*HP_TO_KW*0.5 +
            other*1*HP_TO_KW*0.5
        )

        ws_scope2 = transport + kwh*grid_ef

    ws_total = ws_scope1 + ws_scope2
    st.metric("Total WS", round(ws_total,2))


# =========================================================
# 🌍 FINAL DASHBOARD
# =========================================================
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

st.metric("Total Emissions", round(sw_total+lw_total+ws_total,2))
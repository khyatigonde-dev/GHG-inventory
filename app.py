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
# TABS
# -------------------------
tab1, tab2, tab3 = st.tabs(["🗑️ Solid Waste", "💧 Liquid Waste", "🚰 Water"])

# =========================================================
# 🗑️ SOLID WASTE
# =========================================================
with tab1:

    st.header("Solid Waste")

    # -------------------------
    # SCOPE 1
    # -------------------------
    with st.expander("Scope 1 Inputs", expanded=True):

        # TRANSPORT
        st.subheader("🚛 Transport (Fossil)")
        fossil_vehicles = st.number_input("Vehicles", 0, 1000, 80)
        distance = st.number_input("Distance (km/day)", 0, 200, 50)
        fuel_eff = st.number_input("Fuel (L/km)", 0.0, 1.0, 0.3)

        fuel_used = fossil_vehicles * distance * fuel_eff
        transport_s1 = to_co2e(co2=fuel_used * 2.68)

        # LIVESTOCK
        st.subheader("🐄 Livestock")
        dairy = st.number_input("Dairy", 0, 100000, 2000)
        nondairy = st.number_input("Non-dairy", 0, 100000, 7000)
        young = st.number_input("Young", 0, 100000, 1000)

        livestock = to_co2e(
            ch4=(dairy*0.1096 + nondairy*0.0526 + young*0.0197)
        )

        # GVP
        st.subheader("🗑️ GVP")
        waste = st.number_input("Waste (TPD)", 0.0, 10000.0, 130.0)
        uncol_pct = st.slider("Uncollected %", 0, 100, 20)
        burn_pct = st.slider("Burn %", 0, 100, 30)

        uncol = waste*(uncol_pct/100)
        burned = uncol*(burn_pct/100)
        dumped = uncol - burned

        gvp = to_co2e(
            co2=burned*1.4,
            ch4=dumped*0.4,
            bc=burned*1
        )

        # COMPOSTING
        st.subheader("♻️ Composting")
        comp_waste = st.number_input("Compost Waste", 0.0, 10000.0, 72.0)
        comp_fuel = st.number_input("Fuel (L/day)", 0.0, 10000.0, 0.0)

        comp_emissions = to_co2e(
            co2=comp_fuel*2.68,
            ch4=comp_waste*0.004,
            n2o=comp_waste*0.0003
        )

        # INCINERATION
        st.subheader("🔥 Incineration")
        inc_waste = st.number_input("Incineration Waste", 0.0, 10000.0, 0.0)
        inc_fuel = st.number_input("Fuel (L/day)", 0.0, 10000.0, 0.0)

        inc_emissions = to_co2e(
            co2=inc_fuel*2.68 + inc_waste*1.2,
            ch4=inc_waste*0.0005,
            n2o=inc_waste*0.0002,
            bc=inc_waste*0.02
        )

        # DISPOSAL
        st.subheader("🪦 Disposal")
        disp_waste = st.number_input("Disposal Waste", 0.0, 10000.0, 50.0)
        disp_ch4 = disp_waste * 0.15 * 0.5 * 0.6 * 0.5
        disp_emissions = to_co2e(ch4=disp_ch4)

        sw_scope1 = (
            transport_s1 +
            livestock +
            gvp +
            comp_emissions +
            inc_emissions +
            disp_emissions
        )

    # -------------------------
    # SCOPE 2
    # -------------------------
    with st.expander("Scope 2 Inputs"):

        st.subheader("⚡ EV Transport")
        ev_vehicles = st.number_input("EV Vehicles", 0, 1000, 20)
        ev_eff = st.number_input("kWh/km", 0.0, 5.0, 0.8)

        sw_scope2 = ev_vehicles * distance * ev_eff * grid_ef

    sw_total = sw_scope1 + sw_scope2

    st.metric("Total Solid Waste", round(sw_total,2))


# =========================================================
# 💧 LIQUID WASTE
# =========================================================
with tab2:

    st.header("Liquid Waste")

    with st.expander("Scope 1 Inputs"):

        septic_pop = st.number_input("Septic Population", 0, 1000000, 500000)
        septic = to_co2e(ch4=septic_pop*0.06*0.6*0.5)

        drain_len = st.number_input("Drain Length", 0, 100000, 10000)
        drain_area = st.number_input("Area", 0.0, 10.0, 0.5)

        drain_ch4 = drain_len*drain_area*0.05*0.6*0.2
        drain = to_co2e(ch4=drain_ch4)

        lw_scope1 = septic + drain + transport_s1

    with st.expander("Scope 2 Inputs"):
        lw_scope2 = 5000 * grid_ef

    lw_total = lw_scope1 + lw_scope2
    st.metric("Total Liquid Waste", round(lw_total,2))


# =========================================================
# 🚰 WATER
# =========================================================
with tab3:

    st.header("Water Supply")

    with st.expander("Scope 1 Inputs"):
        ws_vehicles = st.number_input("Vehicles", 0, 1000, 50)
        ws_scope1 = ws_vehicles * distance * fuel_eff * 2.68

    with st.expander("Scope 2 Inputs"):
        buildings = st.number_input("Buildings", 0, 1000000, 16000)

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
    st.metric("Total Water", round(ws_total,2))


# =========================================================
# 🌍 FINAL DASHBOARD
# =========================================================
st.header("🌍 Overall")

grand_total = sw_total + lw_total + ws_total

df = pd.DataFrame({
    "Sector":["SW","LW","WS"],
    "Scope1":[sw_scope1,lw_scope1,ws_scope1],
    "Scope2":[sw_scope2,lw_scope2,ws_scope2],
    "Total":[sw_total,lw_total,ws_total]
})

st.dataframe(df)

st.plotly_chart(px.bar(df, x="Sector", y=["Scope1","Scope2"], barmode="group"))
st.plotly_chart(px.pie(df, values="Total", names="Sector"))

st.metric("Total Emissions", round(grand_total,2))
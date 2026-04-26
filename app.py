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

factors = {
    "diesel": {"energy": 36.372, "CO2": 0.0741, "CH4": 0.000039, "N2O": 0.000039, "BC": 0.0234},
    "natural_gas": {"energy": 0.0333, "CO2": 0.0561, "CH4": 0.000092, "N2O": 0.000003, "BC": 0.00005},
    "electricity": {"energy": 0, "CO2": 0, "CH4": 0, "N2O": 0, "BC": 0}
}

# -------------------------
# FUNCTIONS
# -------------------------
def calculate_emissions(fuel, fuel_type):
    f = factors[fuel_type]

    if fuel_type == "electricity":
        return 0, 0, 0, 0, 0

    co2 = fuel * f["energy"] * f["CO2"]
    ch4 = fuel * f["energy"] * f["CH4"]
    n2o = fuel * f["energy"] * f["N2O"]
    bc = fuel * f["BC"]

    total = (
        co2 * gwp["CO2"] +
        ch4 * gwp["CH4"] +
        n2o * gwp["N2O"] +
        bc * gwp["BC"]
    )

    return total, co2, ch4, n2o, bc


def fleet_emissions(vehicles, distance, efficiency, fuel_mix):
    total = 0
    co2 = ch4 = n2o = bc = 0

    for fuel_type, share in fuel_mix.items():
        fuel_used = vehicles * distance * efficiency * (share / 100)
        t, c, ch, n, b = calculate_emissions(fuel_used, fuel_type)

        total += t
        co2 += c
        ch4 += ch
        n2o += n
        bc += b

    return total, co2, ch4, n2o, bc


def processing_emissions(waste, fuel, fuel_type):
    return calculate_emissions(waste * fuel, fuel_type)


# -------------------------
# INPUT SECTION
# -------------------------
with st.expander("📥 Input Parameters", expanded=False):

    st.subheader("🗑️ Solid Waste + Transport")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_waste = st.number_input("Total Waste (TPD)", 0, 10000, 500)
        collected_waste = st.number_input("Collected Waste (TPD)", 0, 10000, 450)
        organic_waste = st.number_input("Organic Waste (TPD)", 0, 10000, 250)

    with col2:
        d2d_vehicles = st.number_input("D2D Vehicles", 0, 1000, 100)
        d2d_distance = st.number_input("Distance (km/day)", 0, 200, 50)
        d2d_efficiency = st.number_input("Fuel (L/km)", 0.0, 1.0, 0.3)

        sw_vehicles = st.number_input("Sweeping Vehicles", 0, 1000, 50)
        sw_distance = st.number_input("Sweeping Distance (km/day)", 0, 200, 40)
        sw_efficiency = st.number_input("Sweeping Fuel (L/km)", 0.0, 1.0, 0.25)

    with col3:
        diesel_pct = st.slider("Diesel %", 0, 100, 70)
        cng_pct = st.slider("CNG %", 0, 100, 10)
        electric_pct = st.slider("Electric %", 0, 100, 20)

    st.subheader("🏭 Processing")
    compost_waste = st.number_input("Compost Waste (TPD)", 0, 10000, 200)
    compost_fuel = st.number_input("Compost Fuel (L/day)", 0, 10000, 100)
    inc_waste = st.number_input("Incineration Waste (TPD)", 0, 10000, 100)
    inc_fuel = st.number_input("Incineration Fuel (L/day)", 0, 10000, 80)

    st.subheader("🐄 Livestock + GVP")
    dairy_count = st.number_input("Dairy Cattle", 0, 1000000, 2000)
    nondairy_count = st.number_input("Non-dairy Cattle", 0, 1000000, 7000)
    young_count = st.number_input("Young Stock", 0, 1000000, 1000)

    uncollected_pct = st.slider("Uncollected Waste (%)", 0, 100, 20)
    burn_pct = st.slider("Burning (%)", 0, 100, 30)

    st.subheader("💧 Liquid Waste")
    septic_population = st.number_input("Septic Population", 0, 10000000, 500000)
    drain_population = st.number_input("Drain Population", 0, 10000000, 300000)

    st.subheader("🚰 Water Supply")
    total_buildings = st.number_input("Total Buildings", 0, 1000000, 16000)
    ws_electricity = st.number_input("Water Electricity (kWh/day)", 0, 1000000, 10000)

# -------------------------
# CALCULATIONS
# -------------------------
fuel_mix = {
    "diesel": diesel_pct,
    "natural_gas": cng_pct,
    "electricity": electric_pct
}

d2d_total, *_ = fleet_emissions(d2d_vehicles, d2d_distance, d2d_efficiency, fuel_mix)
sw_total_fleet, *_ = fleet_emissions(sw_vehicles, sw_distance, sw_efficiency, fuel_mix)

comp_total, *_ = processing_emissions(compost_waste, compost_fuel, "diesel")
inc_total, *_ = processing_emissions(inc_waste, inc_fuel, "diesel")

# Livestock
EF_DAIRY, EF_NONDAIRY, EF_YOUNG = 0.1096, 0.0526, 0.0197
livestock_ch4 = (dairy_count * EF_DAIRY +
                 nondairy_count * EF_NONDAIRY +
                 young_count * EF_YOUNG)
livestock_co2e = livestock_ch4 * gwp["CH4"]

# GVP
EF_CO2, EF_CH4, EF_BC = 1.4, 0.4, 1.0
uncollected = total_waste * (uncollected_pct / 100)
burned = uncollected * (burn_pct / 100)
dumped = uncollected - burned

gvp_co2e = (
    burned * EF_CO2 * gwp["CO2"] +
    (burned + dumped) * EF_CH4 * gwp["CH4"] +
    burned * EF_BC * gwp["BC"]
)

# Liquid waste
BOD, B0 = 0.06, 0.6
septic = septic_population * BOD * B0 * 0.5 * gwp["CH4"]
drains = drain_population * BOD * B0 * 0.2 * gwp["CH4"]

# Water
low = total_buildings * 0.1
bungalow = total_buildings * 0.8
other = total_buildings * 0.1

water_elec = (
    low * 1 * HP_TO_KW * 2 +
    bungalow * 0.5 * HP_TO_KW * 0.5 +
    other * 1 * HP_TO_KW * 0.5
)

water_co2e = water_elec * grid_ef

# FINAL TOTALS
sw_total = d2d_total + sw_total_fleet + comp_total + inc_total + livestock_co2e + gvp_co2e
lw_total = septic + drains
ws_total = water_co2e

grand_total = sw_total + lw_total + ws_total

# -------------------------
# DASHBOARD
# -------------------------
st.markdown("---")
st.header("📊 Results")

col1, col2, col3 = st.columns(3)
col1.metric("Solid Waste", round(sw_total, 2))
col2.metric("Liquid Waste", round(lw_total, 2))
col3.metric("Water Supply", round(ws_total, 2))

st.metric("Total Emissions", round(grand_total, 2))

# Chart
df = pd.DataFrame({
    "Sector": ["Solid Waste", "Liquid Waste", "Water Supply"],
    "Emissions": [sw_total, lw_total, ws_total]
})

st.plotly_chart(px.bar(df, x="Sector", y="Emissions"), use_container_width=True)
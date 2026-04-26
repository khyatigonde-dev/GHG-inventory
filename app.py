# -------------------------
# SOLID WASTE - SCOPE 1
# -------------------------

st.header("🗑️ Solid Waste - Scope 1")

# -------------------------
# CONSTANTS
# -------------------------
gwp = {"CO2": 1, "CH4": 28, "N2O": 265, "BC": 590}

def to_co2e(co2=0, ch4=0, n2o=0, bc=0):
    return co2 + ch4*28 + n2o*265 + bc*590

# -------------------------
# TRANSPORT (FOSSIL)
# -------------------------
st.subheader("🚛 Transport")

fossil_vehicles = st.number_input("Fossil Vehicles", 0, 1000, 80)
distance = st.number_input("Distance (km/day)", 0, 200, 50)
fuel_eff = st.number_input("Fuel Consumption (L/km)", 0.0, 1.0, 0.3)

fuel_used = fossil_vehicles * distance * fuel_eff
transport_s1 = to_co2e(co2=fuel_used * 2.68)

# -------------------------
# LIVESTOCK
# -------------------------
st.subheader("🐄 Livestock")

dairy = st.number_input("Dairy Cattle", 0, 100000, 2000)
nondairy = st.number_input("Non-Dairy Cattle", 0, 100000, 7000)
young = st.number_input("Young Stock", 0, 100000, 1000)

livestock = to_co2e(
    ch4=(dairy*0.1096 + nondairy*0.0526 + young*0.0197)
)

# -------------------------
# GVP (UNCONTROLLED WASTE)
# -------------------------
st.subheader("🗑️ Garbage Vulnerable Points (GVP)")

waste = st.number_input("Total Waste (TPD)", 0.0, 10000.0, 130.0)
uncollected_pct = st.slider("Uncollected Waste (%)", 0, 100, 20)
burn_pct = st.slider("Burning (%)", 0, 100, 30)

uncol = waste * (uncollected_pct / 100)
burned = uncol * (burn_pct / 100)
dumped = uncol - burned

gvp = to_co2e(
    co2=burned * 1.4,
    ch4=dumped * 0.4,
    bc=burned * 1
)

# -------------------------
# COMPOSTING
# -------------------------
st.subheader("♻️ Composting")

comp_waste = st.number_input("Waste to Compost (TPD)", 0.0, 10000.0, 72.0)
comp_fuel = st.number_input("Fuel Use (L/day) - Compost", 0.0, 10000.0, 0.0)

comp_emissions = to_co2e(
    co2=comp_fuel * 2.68,
    ch4=comp_waste * 0.004,
    n2o=comp_waste * 0.0003
)

# -------------------------
# INCINERATION
# -------------------------
st.subheader("🔥 Incineration")

inc_waste = st.number_input("Waste to Incineration (TPD)", 0.0, 10000.0, 0.0)
inc_fuel = st.number_input("Fuel Use (L/day) - Incineration", 0.0, 10000.0, 0.0)

inc_emissions = to_co2e(
    co2=inc_fuel * 2.68 + inc_waste * 1.2,
    ch4=inc_waste * 0.0005,
    n2o=inc_waste * 0.0002,
    bc=inc_waste * 0.02
)

# -------------------------
# DISPOSAL (LANDFILL)
# -------------------------
st.subheader("🪦 Waste Disposal")

disp_waste = st.number_input("Waste to Disposal (TPD)", 0.0, 10000.0, 50.0)
disp_mcf = st.number_input("MCF", 0.0, 1.0, 0.6)
disp_doc = st.number_input("DOC", 0.0, 1.0, 0.15)
disp_docf = st.number_input("DOCf", 0.0, 1.0, 0.5)
disp_f = st.number_input("Methane Fraction (F)", 0.0, 1.0, 0.5)
disp_recovery = st.number_input("Methane Recovery", 0.0, 1.0, 0.0)

disp_ch4 = (
    disp_waste *
    disp_doc *
    disp_docf *
    disp_mcf *
    disp_f *
    (1 - disp_recovery)
)

disp_emissions = to_co2e(ch4=disp_ch4)

# -------------------------
# TOTAL SCOPE 1
# -------------------------
sw_scope1 = (
    transport_s1 +
    livestock +
    gvp +
    comp_emissions +
    inc_emissions +
    disp_emissions
)

# -------------------------
# OUTPUT
# -------------------------
st.markdown("---")
st.subheader("📊 Scope 1 Breakdown")

col1, col2, col3 = st.columns(3)
col1.metric("Transport", round(transport_s1, 2))
col2.metric("Livestock", round(livestock, 2))
col3.metric("GVP", round(gvp, 2))

col4, col5, col6 = st.columns(3)
col4.metric("Composting", round(comp_emissions, 2))
col5.metric("Incineration", round(inc_emissions, 2))
col6.metric("Disposal", round(disp_emissions, 2))

st.metric("Total Scope 1 (kg CO₂e/day)", round(sw_scope1, 2))
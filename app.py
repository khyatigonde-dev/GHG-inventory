# =========================================================
# 🗑️ SOLID WASTE (SCOPE 1 + SCOPE 2)
# =========================================================

st.header("🗑️ Solid Waste")

# -------------------------
# CONSTANTS
# -------------------------
gwp = {"CO2": 1, "CH4": 28, "N2O": 265, "BC": 590}
grid_ef = 0.82

def to_co2e(co2=0, ch4=0, n2o=0, bc=0):
    return co2 + ch4*28 + n2o*265 + bc*590

# =========================================================
# 🔹 SCOPE 1 INPUTS + CALC
# =========================================================
with st.expander("Scope 1 (Direct Emissions)", expanded=True):

    # -------------------------
    # TRANSPORT (FOSSIL)
    # -------------------------
    st.subheader("🚛 Transport (Fossil)")

    sw_fossil = st.number_input("Fossil Vehicles", 0, 1000, 80)
    sw_distance = st.number_input("Distance (km/day)", 0, 200, 50)
    sw_fuel_eff = st.number_input("Fuel Consumption (L/km)", 0.0, 1.0, 0.3)

    fuel_used = sw_fossil * sw_distance * sw_fuel_eff
    transport_s1 = to_co2e(co2=fuel_used * 2.68)

    # -------------------------
    # LIVESTOCK
    # -------------------------
    st.subheader("🐄 Livestock")

    dairy = st.number_input("Dairy Cattle", 0, 100000, 2000)
    nondairy = st.number_input("Non-dairy Cattle", 0, 100000, 7000)
    young = st.number_input("Young Stock", 0, 100000, 1000)

    livestock = to_co2e(
        ch4=(dairy*0.1096 + nondairy*0.0526 + young*0.0197)
    )

    # -------------------------
    # GVP
    # -------------------------
    st.subheader("🗑️ Garbage Vulnerable Points (GVP)")

    waste = st.number_input("Total Waste (TPD)", 0.0, 10000.0, 130.0)
    uncol_pct = st.slider("Uncollected Waste (%)", 0, 100, 20)
    burn_pct = st.slider("Burning (%)", 0, 100, 30)

    uncol = waste * (uncol_pct / 100)
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
    comp_fuel = st.number_input("Fuel Use (L/day)", 0.0, 10000.0, 0.0)

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
    inc_fuel = st.number_input("Fuel Use (L/day)", 0.0, 10000.0, 0.0)

    inc_emissions = to_co2e(
        co2=inc_fuel * 2.68 + inc_waste * 1.2,
        ch4=inc_waste * 0.0005,
        n2o=inc_waste * 0.0002,
        bc=inc_waste * 0.02
    )

    # -------------------------
    # DISPOSAL
    # -------------------------
    st.subheader("🪦 Waste Disposal")

    disp_waste = st.number_input("Waste to Disposal (TPD)", 0.0, 10000.0, 50.0)

    disp_ch4 = disp_waste * 0.15 * 0.5 * 0.6 * 0.5
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

# =========================================================
# 🔹 SCOPE 2 INPUTS + CALC
# =========================================================
with st.expander("Scope 2 (Indirect Emissions)"):

    # -------------------------
    # EV TRANSPORT
    # -------------------------
    st.subheader("⚡ EV Transport")

    sw_ev = st.number_input("EV Vehicles", 0, 1000, 20)
    sw_ev_eff = st.number_input("EV Efficiency (kWh/km)", 0.0, 5.0, 0.8)

    transport_s2 = sw_ev * sw_distance * sw_ev_eff * grid_ef

    # -------------------------
    # ELECTRICITY
    # -------------------------
    st.subheader("⚡ Processing & Facilities")

    comp_kwh = st.number_input("Composting Electricity (kWh/day)", 0, 100000, 1000)
    inc_kwh = st.number_input("Incineration Electricity (kWh/day)", 0, 100000, 2000)
    mrf_kwh = st.number_input("MRF Electricity (kWh/day)", 0, 100000, 1500)
    disp_kwh = st.number_input("Disposal Electricity (kWh/day)", 0, 100000, 1000)

    comp_elec = comp_kwh * grid_ef
    inc_elec = inc_kwh * grid_ef
    mrf_elec = mrf_kwh * grid_ef
    disp_elec = disp_kwh * grid_ef

    # -------------------------
    # TOTAL SCOPE 2
    # -------------------------
    sw_scope2 = (
        transport_s2 +
        comp_elec +
        inc_elec +
        mrf_elec +
        disp_elec
    )

# =========================================================
# 📊 OUTPUT
# =========================================================
st.markdown("---")
st.subheader("📊 Solid Waste Emissions")

col1, col2 = st.columns(2)

with col1:
    st.metric("Scope 1 (kg CO₂e/day)", round(sw_scope1, 2))

with col2:
    st.metric("Scope 2 (kg CO₂e/day)", round(sw_scope2, 2))

sw_total = sw_scope1 + sw_scope2

st.metric("Total Solid Waste Emissions", round(sw_total, 2))

# =========================================================
# 💧 LIQUID WASTE (SCOPE 1 + SCOPE 2)
# =========================================================

st.header("💧 Liquid Waste")

# -------------------------
# CONSTANTS
# -------------------------
gwp = {"CO2": 1, "CH4": 28, "N2O": 265}
grid_ef = 0.82

def to_co2e(co2=0, ch4=0, n2o=0):
    return co2 + ch4*28 + n2o*265

B0 = 0.6

# =========================================================
# 🔹 SCOPE 1
# =========================================================
with st.expander("Scope 1 (Direct Emissions)", expanded=True):

    # -------------------------
    # CONTAINMENT
    # -------------------------
    st.subheader("🚽 Containment")

    col1, col2 = st.columns(2)

    with col1:
        sewer_qty = st.number_input("Sewer Waste (m³/day)", 0.0, 100000.0, 1000.0)
        sewer_ef = st.number_input("Sewer EF", 0.0, 1.0, 0.01)

    with col2:
        pit_qty = st.number_input("Pit Latrine Waste (m³/day)", 0.0, 100000.0, 500.0)
        pit_ef = st.number_input("Pit EF", 0.0, 1.0, 0.2)

    # Septic tank (your formula)
    septic_pop = st.number_input("Septic Population", 0, 10000000, 500000)
    septic_ch4 = septic_pop * 0.06 * B0 * 0.1  # BOD * B0 * MCF

    # Open drains (length × area)
    st.subheader("🌊 Open Drains")

    drain_length = st.number_input("Drain Length (m)", 0, 100000, 10000)
    drain_area = st.number_input("Cross-sectional Area (m²)", 0.0, 10.0, 0.5)
    drain_bod = st.number_input("BOD (kg/m³)", 0.0, 10.0, 0.05)

    drain_volume = drain_length * drain_area
    tow = drain_volume * drain_bod
    drain_ch4 = tow * B0 * 0.2

    # Convert containment
    sewer = to_co2e(ch4=sewer_qty * sewer_ef)
    pit = to_co2e(ch4=pit_qty * pit_ef)
    septic = to_co2e(ch4=septic_ch4)
    drain = to_co2e(ch4=drain_ch4)

    containment = sewer + pit + septic + drain

    # -------------------------
    # TRANSPORT (FOSSIL)
    # -------------------------
    st.subheader("🚛 Transport (Fossil)")

    lw_fossil = st.number_input("Fossil Vehicles (LW)", 0, 1000, 50)
    lw_distance = st.number_input("Distance (km/day)", 0, 200, 40)
    lw_fuel_eff = st.number_input("Fuel (L/km)", 0.0, 1.0, 0.3)

    fuel_used = lw_fossil * lw_distance * lw_fuel_eff
    transport_s1 = to_co2e(co2=fuel_used * 2.68)

    # -------------------------
    # TREATMENT
    # -------------------------
    st.subheader("🧪 Treatment")

    bod = st.number_input("BOD Load (kg/day)", 0.0, 100000.0, 5000.0)
    n_load = st.number_input("Nitrogen Load (kg/day)", 0.0, 100000.0, 1000.0)

    ch4_treat = bod * B0 * 0.25   # anaerobic EF
    n2o_treat = n_load * 0.005

    treatment = to_co2e(ch4=ch4_treat, n2o=n2o_treat)

    # -------------------------
    # TOTAL SCOPE 1
    # -------------------------
    lw_scope1 = containment + transport_s1 + treatment


# =========================================================
# 🔹 SCOPE 2
# =========================================================
with st.expander("Scope 2 (Indirect Emissions)"):

    # -------------------------
    # EV TRANSPORT
    # -------------------------
    st.subheader("⚡ EV Transport")

    lw_ev = st.number_input("EV Vehicles (LW)", 0, 1000, 10)
    lw_ev_eff = st.number_input("EV Efficiency (kWh/km)", 0.0, 5.0, 0.8)

    transport_s2 = lw_ev * lw_distance * lw_ev_eff * grid_ef

    # -------------------------
    # TREATMENT ELECTRICITY
    # -------------------------
    st.subheader("⚡ Treatment Electricity")

    lw_kwh = st.number_input("Treatment Electricity (kWh/day)", 0, 100000, 5000)
    treatment_elec = lw_kwh * grid_ef

    # -------------------------
    # TOTAL SCOPE 2
    # -------------------------
    lw_scope2 = transport_s2 + treatment_elec


# =========================================================
# 📊 OUTPUT
# =========================================================
st.markdown("---")
st.subheader("📊 Liquid Waste Emissions")

col1, col2 = st.columns(2)

with col1:
    st.metric("Scope 1 (kg CO₂e/day)", round(lw_scope1, 2))

with col2:
    st.metric("Scope 2 (kg CO₂e/day)", round(lw_scope2, 2))

lw_total = lw_scope1 + lw_scope2

st.metric("Total Liquid Waste Emissions", round(lw_total, 2))

# =========================================================
# 🚰 WATER SUPPLY (SCOPE 1 + SCOPE 2)
# =========================================================

st.header("🚰 Water Supply")

# -------------------------
# CONSTANTS
# -------------------------
grid_ef = 0.82
HP_TO_KW = 0.746

# =========================================================
# 🔹 SCOPE 1
# =========================================================
with st.expander("Scope 1 (Direct Emissions)", expanded=True):

    st.subheader("🚛 Water Transmission (Fossil Tankers)")

    ws_fossil = st.number_input("Fossil Tankers", 0, 1000, 40)
    ws_distance = st.number_input("Distance per tanker (km/day)", 0, 200, 40)
    ws_fuel_eff = st.number_input("Fuel Consumption (L/km)", 0.0, 1.0, 0.3)

    fuel_used_ws = ws_fossil * ws_distance * ws_fuel_eff

    ws_scope1 = fuel_used_ws * 2.68  # kg CO2e/day

# =========================================================
# 🔹 SCOPE 2
# =========================================================
with st.expander("Scope 2 (Indirect Emissions)", expanded=True):

    # -------------------------
    # EV TRANSPORT
    # -------------------------
    st.subheader("⚡ EV Water Tankers")

    ws_ev = st.number_input("EV Tankers", 0, 1000, 10)
    ws_ev_eff = st.number_input("EV Efficiency (kWh/km)", 0.0, 5.0, 0.8)

    ws_transport_s2 = ws_ev * ws_distance * ws_ev_eff * grid_ef

    # -------------------------
    # DISTRIBUTION (PUMPING STATIONS)
    # -------------------------
    st.subheader("⚡ Distribution (Pumping Stations)")

    dist_count = st.number_input("No. of Pumping Stations", 0, 1000, 50)
    dist_hp = st.number_input("Pump Power (HP)", 0.0, 500.0, 50.0)
    dist_hours = st.number_input("Operating Hours/day", 0.0, 24.0, 8.0)

    dist_kwh = dist_count * (dist_hp * HP_TO_KW) * dist_hours
    dist_emissions = dist_kwh * grid_ef

    # -------------------------
    # STORAGE (ESR + SUMP)
    # -------------------------
    st.subheader("⚡ Storage Infrastructure")

    col1, col2 = st.columns(2)

    with col1:
        esr_count = st.number_input("No. of ESR", 0, 1000, 20)
        esr_hp = st.number_input("ESR Pump HP", 0.0, 500.0, 30.0)
        esr_hours = st.number_input("ESR Operating Hours", 0.0, 24.0, 6.0)

    with col2:
        sump_count = st.number_input("No. of Sumps", 0, 1000, 20)
        sump_hp = st.number_input("Sump Pump HP", 0.0, 500.0, 25.0)
        sump_hours = st.number_input("Sump Operating Hours", 0.0, 24.0, 6.0)

    esr_kwh = esr_count * (esr_hp * HP_TO_KW) * esr_hours
    sump_kwh = sump_count * (sump_hp * HP_TO_KW) * sump_hours

    storage_kwh = esr_kwh + sump_kwh
    storage_emissions = storage_kwh * grid_ef

    # -------------------------
    # WATER TREATMENT PLANT (WTP)
    # -------------------------
    st.subheader("⚡ Water Treatment Plant")

    wtp_kwh = st.number_input("WTP Electricity (kWh/day)", 0, 1000000, 10000)
    wtp_emissions = wtp_kwh * grid_ef

    # -------------------------
    # BACKUP POWER (DG SET)
    # -------------------------
    st.subheader("⚡ Backup Power")

    dg_fuel = st.number_input("Diesel Consumption (L/day)", 0, 10000, 500)
    dg_emissions = dg_fuel * 2.68

    # -------------------------
    # BUILDING-LEVEL PUMPING
    # -------------------------
    st.subheader("🏘️ Building-Level Pumping")

    total_buildings = st.number_input("Total Buildings", 0, 1000000, 16000)

    low_pct = 0.1
    bungalow_pct = 0.8
    other_pct = 0.1

    low_count = total_buildings * low_pct
    bungalow_count = total_buildings * bungalow_pct
    other_count = total_buildings * other_pct

    col1, col2, col3 = st.columns(3)

    with col1:
        low_hp = st.number_input("Low-rise HP", 0.0, 50.0, 1.0)
        low_hours = st.number_input("Low-rise Hours", 0.0, 24.0, 2.0)

    with col2:
        bungalow_hp = st.number_input("Bungalow HP", 0.0, 50.0, 0.5)
        bungalow_hours = st.number_input("Bungalow Hours", 0.0, 24.0, 0.5)

    with col3:
        other_hp = st.number_input("Other HP", 0.0, 50.0, 1.0)
        other_hours = st.number_input("Other Hours", 0.0, 24.0, 0.5)

    low_kwh = low_count * (low_hp * HP_TO_KW) * low_hours
    bungalow_kwh = bungalow_count * (bungalow_hp * HP_TO_KW) * bungalow_hours
    other_kwh = other_count * (other_hp * HP_TO_KW) * other_hours

    building_kwh = low_kwh + bungalow_kwh + other_kwh
    building_emissions = building_kwh * grid_ef

    # -------------------------
    # TOTAL SCOPE 2
    # -------------------------
    ws_scope2 = (
        ws_transport_s2 +
        dist_emissions +
        storage_emissions +
        wtp_emissions +
        dg_emissions +
        building_emissions
    )

# =========================================================
# 📊 OUTPUT
# =========================================================
st.markdown("---")
st.subheader("📊 Water Supply Emissions")

col1, col2 = st.columns(2)

with col1:
    st.metric("Scope 1 (kg CO₂e/day)", round(ws_scope1, 2))

with col2:
    st.metric("Scope 2 (kg CO₂e/day)", round(ws_scope2, 2))

ws_total = ws_scope1 + ws_scope2

st.metric("Total Water Supply Emissions", round(ws_total, 2))
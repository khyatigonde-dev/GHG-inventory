st.subheader("📊 Sector-wise Total Emissions Comparison")

# Split SW into core + localization
sw_localization = gvp + livestock
sw_core = sw_total - sw_localization

df_total = pd.DataFrame({
    "Category": [
        "SW - Core",
        "SW - Localization (GVP + Livestock)",
        "Liquid Waste",
        "Water Supply"
    ],
    "Emissions": [
        sw_core,
        sw_localization,
        lw_total,
        ws_total
    ]
})

st.plotly_chart(
    px.bar(
        df_total,
        x="Category",
        y="Emissions",
        title="Sector-wise Emissions with SW Localization (kg CO₂e/day)"
    ),
    use_container_width=True
)
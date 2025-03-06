import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configure Streamlit page
st.set_page_config(page_title="CBAM Calculator Dashboard", page_icon="🌍", layout="wide")
st.title("🌍 CBAM Calculator Dashboard")

# Load the static CSV file (ensure it's in the same folder as this script)
CSV_FILE_PATH = "Iron Emission Factors.csv"
df = pd.read_csv(CSV_FILE_PATH)

# Create 5 columns for inputs on one row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    unique_cn_codes = sorted(df["CN Code"].unique())
    default_cn_code = "7201"
    default_cn_index = unique_cn_codes.index(default_cn_code) if default_cn_code in unique_cn_codes else 0
    selected_cn_code = st.selectbox("CN Code", unique_cn_codes, index=default_cn_index)

with col2:
    quantity = st.number_input("Quantity (Tonnes)", min_value=0.0, value=150.0, step=1.0)

with col3:
    unique_countries = sorted(df["Country"].unique())
    default_country = "India"
    default_country_index = unique_countries.index(default_country) if default_country in unique_countries else 0
    selected_country = st.selectbox("Country", unique_countries, index=default_country_index)

with col4:
    default_comp_country = "South Korea"
    default_comp_country_index = unique_countries.index(default_comp_country) if default_comp_country in unique_countries else 0
    selected_comp_country = st.selectbox("Comparison Country", unique_countries, index=default_comp_country_index)

with col5:
    carbon_price = st.number_input("Carbon Price (Euros)", min_value=0.0, value=75.51, step=0.01)

# Display the CN Code description across the full width
description_for_cn = df.loc[df["CN Code"] == selected_cn_code, "Description"].unique()
if description_for_cn.size > 0:
    st.markdown(f"**CN Code Description: {description_for_cn[0]}**")
else:
    st.markdown("**CN Code Description: Not available**")

def get_value_for_type(df_country, typ):
    row = df_country[df_country["Type"].str.lower() == typ.lower()]
    if not row.empty:
        return row.iloc[0]["Value"]
    else:
        return None

# Filter data for the selected countries
df_country1 = df[(df["CN Code"] == selected_cn_code) & (df["Country"] == selected_country)]
df_country2 = df[(df["CN Code"] == selected_cn_code) & (df["Country"] == selected_comp_country)]

if df_country1.empty:
    st.warning(f"No data found for CN Code {selected_cn_code} in {selected_country}.")
if df_country2.empty:
    st.warning(f"No data found for CN Code {selected_cn_code} in {selected_comp_country}.")

if not df_country1.empty and not df_country2.empty:
    # Calculations for Country 1
    direct_value1 = get_value_for_type(df_country1, "Direct")
    indirect_value1 = get_value_for_type(df_country1, "Indirect")
    total_value1 = get_value_for_type(df_country1, "Total")
    
    direct_emissions1 = direct_value1 * quantity if direct_value1 is not None else 0
    indirect_emissions1 = indirect_value1 * quantity if indirect_value1 is not None else 0
    total_emissions1 = total_value1 * quantity if total_value1 is not None else 0
    total_cbam_costs1 = total_emissions1 * carbon_price
    
    # Calculations for Country 2
    direct_value2 = get_value_for_type(df_country2, "Direct")
    indirect_value2 = get_value_for_type(df_country2, "Indirect")
    total_value2 = get_value_for_type(df_country2, "Total")
    
    direct_emissions2 = direct_value2 * quantity if direct_value2 is not None else 0
    indirect_emissions2 = indirect_value2 * quantity if indirect_value2 is not None else 0
    total_emissions2 = total_value2 * quantity if total_value2 is not None else 0
    total_cbam_costs2 = total_emissions2 * carbon_price

    # --- New Feature: Best Alternative Country ---
    all_total = df[(df["CN Code"] == selected_cn_code) & (df["Type"].str.lower() == "total")]
    all_total = all_total[all_total["Value"] > 0]
    all_total = all_total[~all_total["Country"].isin([selected_country, selected_comp_country])]
    if not all_total.empty:
        best_row = all_total.loc[all_total["Value"].idxmin()]
        best_alternative_country = best_row["Country"]
        df_best_alt = df[(df["CN Code"] == selected_cn_code) & (df["Country"] == best_alternative_country)]
        best_direct = get_value_for_type(df_best_alt, "Direct")
        best_indirect = get_value_for_type(df_best_alt, "Indirect")
        best_total = get_value_for_type(df_best_alt, "Total")
        best_direct_emissions = best_direct * quantity if best_direct is not None else 0
        best_indirect_emissions = best_indirect * quantity if best_indirect is not None else 0
        best_total_emissions = best_total * quantity if best_total is not None else 0
        best_total_cbam_costs = best_total_emissions * carbon_price
    else:
        best_alternative_country = "N/A"
        best_direct_emissions = best_indirect_emissions = best_total_emissions = best_total_cbam_costs = 0

    st.markdown("<hr style='margin: 40px 0;'>", unsafe_allow_html=True)
    
    # --- Layout: First Row with Three Columns ---
    # Column 1: Country 1 card and below it the Best Alternative card.
    # Column 2: Country 2 card.
    # Column 3: Chart.
    col_country1, col_country2, col_chart = st.columns(3)
    
    card_template = """
    <div style="background-color: #222; color: #fff; padding: 20px; border-radius: 8px; margin: 10px;">
        <h3 style="font-size: 20px; margin-bottom: 10px;">Emission costs for {title}</h3>
        <p style="font-size: 18px; margin: 0;">Direct Emissions: {direct:.0f} Tonne CO2E</p>
        <p style="font-size: 18px; margin: 0;">Indirect Emissions: {indirect:.0f} Tonne CO2E</p>
        <p style="font-size: 18px; margin: 0;">Total Emissions: {total:.0f} Tonne CO2E</p>
        <p style="font-size: 18px; margin: 0;">Total CBAM costs: {cbam:,.0f} Euros</p>
    </div>
    """
    
    with col_country1:
        st.markdown(card_template.format(
            title=selected_country,
            direct=direct_emissions1,
            indirect=indirect_emissions1,
            total=total_emissions1,
            cbam=total_cbam_costs1
        ), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:18px; color: #fff;'>Based on the calculated emissions, we have determined the best alternative country (with the lowest emissions) for importing this item.</p>", unsafe_allow_html=True)
        if best_alternative_country != "N/A":
            st.markdown(card_template.format(
                title=best_alternative_country,
                direct=best_direct_emissions,
                indirect=best_indirect_emissions,
                total=best_total_emissions,
                cbam=best_total_cbam_costs
            ), unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #222; color: #fff; padding: 20px; border-radius: 8px; margin: 10px;'>"
                        "<h3 style='font-size: 20px; margin-bottom: 10px;'>Best Alternative</h3>"
                        "<p style='font-size: 18px; margin: 0;'>No alternative found</p></div>", unsafe_allow_html=True)
    
    with col_country2:
        st.markdown(card_template.format(
            title=selected_comp_country,
            direct=direct_emissions2,
            indirect=indirect_emissions2,
            total=total_emissions2,
            cbam=total_cbam_costs2
        ), unsafe_allow_html=True)
    
    with col_chart:
        if best_alternative_country != "N/A":
            x_values = [selected_country, selected_comp_country, best_alternative_country]
            direct_y = [direct_emissions1, direct_emissions2, best_direct_emissions]
            indirect_y = [indirect_emissions1, indirect_emissions2, best_indirect_emissions]
        else:
            x_values = [selected_country, selected_comp_country]
            direct_y = [direct_emissions1, direct_emissions2]
            indirect_y = [indirect_emissions1, indirect_emissions2]
            
        fig = go.Figure(data=[
            go.Bar(
                name='Direct Emissions',
                x=x_values,
                y=direct_y,
                width=[0.3] * len(x_values),
                text=[f"{val:.0f}" for val in direct_y],
                textposition="auto",
                textfont=dict(size=12),
                marker_color='blue'
            ),
            go.Bar(
                name='Indirect Emissions',
                x=x_values,
                y=indirect_y,
                width=[0.3] * len(x_values),
                text=[f"{val:.0f}" for val in indirect_y],
                textposition="auto",
                textfont=dict(size=12),
                marker_color='orange'
            )
        ])
        fig.update_layout(
            barmode='stack',
            width=938,
            height=563,
            title_text="Direct and Indirect Emissions",
            font=dict(size=12),
            xaxis_title="Country",
            yaxis_title="Emissions (Tonne CO2E)",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

# Add an informational card about CBAM at the end of the dashboard
cbam_info = """
<div style="background-color: #222; color: #fff; padding: 20px; border-radius: 8px; margin-top: 20px;">
    <h3 style="font-size: 20px; margin-bottom: 10px;">About CBAM</h3>
    <p style="font-size: 18px; margin: 0;">
    The Carbon Border Adjustment Mechanism (CBAM) is an extension of the EU Emissions Trading System (EU ETS), designed to ensure that imported goods face the same carbon pricing as those produced within the EU. Under the EU ETS, companies operating in high-emission industries must purchase carbon allowances to cover their emissions. However, imports from countries with weaker carbon regulations do not face similar costs, creating a risk of carbon leakage—where businesses move production outside the EU to avoid carbon pricing. CBAM addresses this by requiring importers of carbon-intensive goods (such as steel, cement, aluminum, fertilizers, electricity, and hydrogen) to report their embedded emissions and purchase CBAM certificates in line with the EU carbon price. This levels the playing field, incentivizes global decarbonization, and strengthens the EU’s climate neutrality goals.
    </p>
    <p style="font-size: 18px; margin-top: 10px;">
    Source: <a href="https://publications.jrc.ec.europa.eu/repository/handle/JRC134682" target="_blank" style="color: #fff; text-decoration: underline;">JRC Technical Report</a>
    </p>
</div>
"""
st.markdown(cbam_info, unsafe_allow_html=True)

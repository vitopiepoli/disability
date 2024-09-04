import streamlit as st
import plotly.express as px
import pandas as pd
import geopandas as gpd

# Define the measures list
measures = ['Residential', 'Day_Care', 'Respite', 'Other', 'Residential_Service',
    'Day_Care_Service', 'Respite_Service', 'Other_Service',
    'Residential_Served', 'Day_Care_Served', 'Respite_Served',
    'Other_Served', 'Residential_Ratio', 'Day_Care_Ratio', 'Respite_Ratio',
    'Other_Ratio']

measure_cost = ['Cost_Residential', 'Cost_Day_Care', 'Cost_Respite',
    'Cost_Other', 'Money_Residential', 'Money_Day_Care', 'Money_Respite',
    'Money_Other', 'Residential_Fund_Ratio', 'Day_Care_Fund_Ratio',
    'Respite_Fund_Ratio', 'Other_Fund_Ratio']

unmet_measures = ['Unmet_Residential', 'Unmet_Day_Care', 'Unmet_Respite',
    'Unmet_Other', 'Residential_Unmet', 'Day_Care_Unmet', 'Respite_Unmet', 'Other_Unmet',
    'Residential_Unmet_Ratio', 'Day_Care_Unmet_Ratio',
    'Respite_Unmet_Ratio', 'Other_Unmet_Ratio',
    'Residential_Fund_Ratio_unmet', 'Day_Care_Fund_Ratio_unmet',
    'Respite_Fund_Ratio_unmet', 'Other_Fund_Ratio_unmet', 'Cost_Residential_unmet',
    'Cost_Day_Care_unmet', 'Cost_Respite_unmet', 'Cost_Other_unmet']

# Function to create a Plotly choropleth map for large numbers
def create_plotly_choropleth_large_numbers(gdf, measure):
    
    
    gdf.index = gdf['ENGLISH']
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color=measure,
        color_continuous_scale="YlGn",
        zoom=5,
        center={"lat": 53.1424, "lon": -7.6921},  # Center of Ireland
        opacity=0.5,
        mapbox_style="open-street-map",
        labels={measure: measure},
        hover_data={
            'ENGLISH': True,  # Show the 'ENGLISH' field
            measure: True  # Show the measure field
        })
    
    # Update the hover template to customize the tooltip
    fig.update_traces(
        hovertemplate="<b>Location:</b> %{customdata[0]}<br>" +
                      "<b>Value:</b> %{z:,.0f}<extra></extra>")
    
    # Function to wrap text every n characters
    def wrap_text(text, n):
        return '<br>'.join([text[i:i+n] for i in range(0, len(text), n)])
    
    # Wrap the legend title every 20 characters
    legend_title = measure
    wrapped_title = wrap_text(legend_title, 20)
    
    # Update the layout with the wrapped legend title
    fig.update_layout(
        coloraxis_colorbar=dict(
            tickformat=',.0f',
            title=wrapped_title
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        width=1200,
        height=600)
    
    # Subset the gdf by the selected measure and the ENGLISH field
    subset_gdf = gdf[[measure]]
    subset_gdf.index.name = 'Location'
    return fig, subset_gdf

# Function to create a Plotly choropleth map for ratios
def create_plotly_choropleth_ratios(gdf, measure, measure_list,word):
    quantiles = gdf[measure].quantile([0.2, 0.4, 0.6, 0.8, 1.0]).values
    
    # Define a custom color scale based on quantiles
    color_scale = [
        [0, 'red'],    # 0th percentile
        [0.2, 'orange'], # 20th percentile
        [0.4, 'yellow'], # 40th percentile
        [0.6, 'lightgreen'], # 60th percentile
        [0.8, 'green'], # 80th percentile
        [1, 'darkgreen']   # 100th percentile
    ]
    
    gdf.index = gdf['ENGLISH']
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color=measure,
        color_continuous_scale=color_scale,
        range_color=(quantiles[0], quantiles[-1]),
        zoom=5,
        center={"lat": 53.1424, "lon": -7.6921},  # Center of Ireland
        opacity=0.5,
        mapbox_style="open-street-map",
        labels={measure: measure},
        hover_data={
            'ENGLISH': True,  # Show the 'ENGLISH' field
            measure: True  # Show the measure field
        })
    
    # Update the hover template to customize the tooltip
    fig.update_traces(
        hovertemplate="<b>Location:</b> %{customdata[0]}<br>" +
                      "<b>Value:</b> %{z:,.2f}<extra></extra>")
    
    # Function to wrap text every n characters
    def wrap_text(text, n):
        return '<br>'.join([text[i:i+n] for i in range(0, len(text), n)])
    
    # Wrap the legend title every 20 characters
    legend_title = measure
    wrapped_title = wrap_text(legend_title, 30)
    
    # Update the layout with the wrapped legend title
    fig.update_layout(
        coloraxis_colorbar=dict(
            tickformat=',.2f',
            title=wrapped_title
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        width=1200,
        height=600)
    
    # Programmatically find related variables
    base_measure = measure.replace(word, '')
    related_measures = [col for col in measure_list if base_measure in col and col != measure]
    subset_gdf = gdf[[ measure] + related_measures]
    # rename index from ENGLIS to Location
    subset_gdf.index.name = 'Location'
    
    
    return fig, subset_gdf

# Function to render the table with selected columns
def render_table(subset_gdf):
    # Render the table
    st.dataframe(subset_gdf)

# Streamlit app
st.title("Choropleth Map Viewer")

# File uploader in the sidebar
uploaded_file = st.sidebar.file_uploader("Upload a GeoJSON file", type="geojson")

def load_geojson(file):
    return gpd.read_file(file)

# Load the file once and store it in session state
if uploaded_file is not None:
    st.session_state['gdf'] = load_geojson(uploaded_file)

# Function to render maps
def render_maps(tab, map_key1, map_key2, measure_list1, measure_list2, measure_key1, measure_key2, button_key, measure_list,word):
    with tab:
        # Initialize session state for maps if not already done
        if map_key1 not in st.session_state:
            st.session_state[map_key1] = None
        if map_key2 not in st.session_state:
            st.session_state[map_key2] = None

        if 'gdf' in st.session_state:
            gdf = st.session_state['gdf']

            # Select measures for the maps
            measure1 = st.selectbox("Select measure for Map 1", measure_list1, key=measure_key1)
            measure2 = st.selectbox("Select measure for Map 2", measure_list2, key=measure_key2)

            # Button to generate maps
            if st.button("Generate Maps", key=button_key):
                # Create Map 1 using create_plotly_choropleth_large_numbers
                fig1, subset_gdf1 = create_plotly_choropleth_large_numbers(gdf, measure1)
                st.session_state[map_key1] = fig1
                st.session_state[f'{map_key1}_table'] = subset_gdf1

                # Create Map 2 using create_plotly_choropleth_ratios
                fig2, subset_gdf2 = create_plotly_choropleth_ratios(gdf, measure2, measure_list,word)
                st.session_state[map_key2] = fig2
                st.session_state[f'{map_key2}_table'] = subset_gdf2

        # Display the maps and tables if they exist in session state
        if st.session_state[map_key1] is not None:
            st.plotly_chart(st.session_state[map_key1])
            render_table(st.session_state[f'{map_key1}_table'])
        
        if st.session_state[map_key2] is not None:
            st.plotly_chart(st.session_state[map_key2])
            render_table(st.session_state[f'{map_key2}_table'])

# Create tabs
tab1, tab2, tab3 = st.tabs(["Services Coverage", "Funding Analysis", "Projections Unmet"])

# Usage in tab1
render_maps(tab1, 'map1', 'map2', [m for m in measures if 'Ratio' not in m], [m for m in measures if 'Ratio' in m], 'measure1', 'measure2', 'generate_maps', measures,"_Ratio")

# Usage in tab2
render_maps(tab2, 'map1c', 'map2c', [m for m in measure_cost if 'Ratio' not in m], [m for m in measure_cost if 'Ratio' in m], 'measure1c', 'measure2c', 'generate_maps_cost', measure_cost,"_Fund_Ratio")

# Usage in tab3
render_maps(tab3, 'map1u', 'map2u', [m for m in unmet_measures if 'Ratio' not in m], [m for m in unmet_measures if 'Ratio' in m], 'measure1u', 'measure2u', 'generate_maps_unmet', unmet_measures,"_Ratio")
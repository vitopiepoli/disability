import json
import plotly.express as px
import pandas as pd
import geopandas as gpd
geojson_file = "/home/vito/Desktop/Disability/Disable2022_wide.geojson"
# Load the GeoJSON file

gdf = gpd.read_file(geojson_file)

gdf.columns

def create_plotly_choropleth(gdf, measure, color_scale='YlGn'):
    gdf.index = gdf['ENGLISH']
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color=measure,
        color_continuous_scale=color_scale,
        zoom=5,
        center={"lat": 53.1424, "lon": -7.6921},  # Center of Ireland
        opacity=0.5,
        mapbox_style="open-street-map",
        labels={measure: measure},
        hover_data={
            'ENGLISH': True,  # Show the 'ENGLISH' field
            measure: True  # Show the 'Day_Care_Fund_Ratio_unmet' field
        }
    )

    # Update the hover template to customize the tooltip
    fig.update_traces(
        hovertemplate="<b>Location:</b> %{customdata[0]}<br>" +
                      "<b>Value:</b> %{z}<extra></extra>"
    )

    # Function to wrap text every n characters
    def wrap_text(text, n):
        return '<br>'.join([text[i:i+n] for i in range(0, len(text), n)])

    # Wrap the legend title every 20 characters
    legend_title = measure
    wrapped_title = wrap_text(legend_title, 20)

    # Update the layout with the wrapped legend title
    fig.update_layout(
        coloraxis_colorbar=dict(
            
            title=wrapped_title
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        width=1200,
        height=600
    )

    # Show the figure
    return fig

    

## funding analysis
gdf.columns

# select columns with cost in the name
cost_cols = [col for col in gdf.columns if 'Cost' in col]
money_cols = [col for col in gdf.columns if 'Money' in col]
fund_ratio_cols = [col for col in gdf.columns if 'Fund_Ratio' in col]
# subset the geodataframe with all the cost and geodata columns
gdf_cost = gdf[cost_cols + money_cols + fund_ratio_cols +['geometry']+['ENGLISH']+['COUNTY']]
# format cost columns by add comma to the thousand

gdf_cost.columns
f = create_plotly_choropleth(gdf, 'Cost_Residential', color_scale='YlGn')
print(type(f))
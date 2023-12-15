import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import geopandas as gpd
import numpy as np


###################*FRONT PAGE*############################
st.set_page_config(layout='wide')

st.title('US Tornado Visualization')
st.write("""
This app visualizes data on US tornadoes from 1950-2021. You can explore the paths of tornadoes on a map, 
see the distribution of tornadoes by year state, and discover the relationship between 
tornado magnitude and injuries or fatalities.
""")

@st.cache_data
def load_data():
    df = pd.read_feather('us_tornado.feather')
    return df

@st.cache_data
def load_geos():
    df = gpd.read_feather('us_states.feather')
    return df

@st.cache_data
def load_sq_mi():
    df = pd.read_csv('sq_mi_agg.csv')
    return df

tornado = load_data()
us_states = load_geos()

####FILTER OPTIONS#####
st.sidebar.title('Filter Options')
states_checkbox = st.sidebar.checkbox('All states', value=True)

#filter for states
if states_checkbox:
    states = tornado['st'].unique().tolist()
    states.sort()
else:
    states = st.sidebar.multiselect('Specific states', options=sorted(tornado['st'].unique().tolist()), default=[])

#filter for magnitude
min_mag, max_mag = tornado['mag'].min(), tornado['mag'].max()
mag_range = st.sidebar.slider('Magnitude Range (-1 is unknown)', min_value=min_mag, max_value=max_mag, value=(min_mag, max_mag))

def filter_tornadoes():
    return tornado[(tornado['st'].isin(states)) & 
                            (tornado['mag'] >= mag_range[0]) & 
                            (tornado['mag'] <= mag_range[1])]



tornado_filter = filter_tornadoes()

#####SUMMARY STATS######
col1, col2, col3 = st.columns(3)

total_tornadoes = tornado_filter.shape[0]
with col1:
    st.metric(label='Total number of tornadoes', value=total_tornadoes)

total_injuries = tornado_filter['inj'].sum()
with col2:
    st.metric(label='Total tornado-related injuries', value=total_injuries)

total_fatalities = tornado_filter['fat'].sum()
with col3:
    st.metric(label='Total tornado-related fatalities', value=total_fatalities)

##US MAP CHART

#beginning with the geo trace
choropleth_trace = go.Choroplethmapbox(geojson=us_states.__geo_interface__, 
                                       locations=us_states.index, 
                                       z=us_states.index,
                                       colorscale=[[0, 'rgb(204, 204, 204)'], [1, 'rgb(204, 204, 204)']],
                                       showscale=False,
                                       marker_opacity=0.5, 
                                       marker_line_width=1, 
                                       marker_line_color='Blue',
                                       hoverinfo='skip')

#this base map should be first in the fig data
data = [choropleth_trace]
years = sorted(tornado['yr'].unique())


def create_trace(lon, lat, mode, color, size, name, hovertemplate, visible):
    return go.Scattermapbox(
        lon=lon,
        lat=lat,
        mode=mode,
        marker=dict(size=size, color=color),
        name=name,
        hovertemplate=hovertemplate,
        visible=visible
    )


marker_size = 4
line_width = 2
colors = {'start': 'Green', 'end': 'Red', 'line': 'Blue'}

data = [choropleth_trace]
for year in years:
    tornado_year = tornado_filter[tornado_filter['yr'] == year]
    tornado_year_non_zero = tornado_year[(tornado_year['elat'] != 0) & (tornado_year['elon'] != 0)]
    tornado_year_zero = tornado_year[(tornado_year['elat'] == 0) & (tornado_year['elon'] == 0)]

    
    if len(tornado_year_non_zero) > 0:
        lons = []
        lats = []
        for _, row in tornado_year_non_zero.iterrows():
            lons.extend([row['slon'], row['elon'], None]) 
            lats.extend([row['slat'], row['elat'], None]) 

        line_trace = create_trace(lons, 
                                lats, 
                                'lines', 
                                colors['line'], 
                                line_width, 
                                str(year), 
                                None, 
                                False)
        
        start_trace = create_trace(tornado_year_non_zero['slon'], 
                                tornado_year_non_zero['slat'], 
                                'markers', 
                                colors['start'], 
                                marker_size, str(year), 
                                'Starting Point', 
                                False)
        
        end_trace = create_trace(tornado_year_non_zero['elon'], 
                                tornado_year_non_zero['elat'], 
                                'markers', 
                                colors['end'], 
                                marker_size, 
                                str(year), 
                                'Ending Point', 
                                False)

        data.extend([line_trace, start_trace, end_trace])

    if len(tornado_year_zero) > 0:
        zero_trace = create_trace(tornado_year_zero['slon'], 
                                tornado_year_zero['slat'], 
                                'markers', 
                                colors['line'], 
                                marker_size, 
                                str(year), 
                                None, 
                                False)
        data.append(zero_trace)

    #This gets our traces and points visible on start up 
    if len(data) > 1 and data[1].name == str(year):
        data[1].visible = True
    if len(data) > 2 and data[2].name == str(year):
        data[2].visible = True
    if len(data) > 3 and data[3].name == str(year):
        data[3].visible = True

steps = []
for i, year in enumerate(years):
    visibility = [True] + [False] * (len(data) - 1)  # Keep the choropleth trace always visible
    for j in range(1, len(data)): 
        if data[j]['name'] == str(year):
            visibility[j] = True
    step = dict(
        method = 'restyle',
        args = ['visible', visibility],
        label = str(year)
    )
    steps.append(step)

sliders = [dict(
    active = 0,
    y=1.15,
    currentvalue = {"prefix": "Year: "},
    steps = steps
)]

layout = go.Layout(
    sliders = sliders,
    title_text = '',
    showlegend = False,
    mapbox = dict(
        style="carto-positron",
        zoom=3, 
        center = {"lat": 37.0902, "lon": -95.7129},
    ),
    autosize=False,
    width=800,
    height=1000,
    margin={"r":0,"t":0,"l":0,"b":0}
)
fig_us = go.Figure(data=data, layout=layout)
st.plotly_chart(fig_us, use_container_width=True)


##YEARLY TORNADO BAR
state_tornadoes = (tornado_filter.groupby(['yr', 'st']).size()
                   .reset_index(name='Total Tornados')
                   .sort_values('Total Tornados', ascending=False)
                   .rename(columns={'yr': 'Year', 'st': 'State'}))
#The chart looks terrible without setting a limit on states to viz
#default when over 15 is the top tornado states
top_states = (state_tornadoes.groupby('State')['Total Tornados'].sum()
              .sort_values(ascending=False)
              .head(8)
              .index.tolist())

# Create a new column 'State Group' where if the state is in the selected states, 
# it keeps its name, otherwise it becomes 'Other'
state_tornadoes['State Group'] = np.where(state_tornadoes['State'].isin(top_states), state_tornadoes['State'], 'Other')

#ensure other is last
state_groups = sorted([state for state in state_tornadoes['State Group'].unique() if state != 'Other']) + ['Other']

# Create the plot
fig_hist = go.Figure()
for state_group in state_groups:
    fig_hist.add_trace(go.Bar(
        x=state_tornadoes[state_tornadoes['State Group'] == state_group]['Year'],
        y=state_tornadoes[state_tornadoes['State Group'] == state_group]['Total Tornados'],
        name=state_group
    ))

fig_hist.update_layout(barmode='stack', coloraxis=dict(colorscale='Viridis'))
fig_hist.update_traces(marker=dict(line=dict(width=0), coloraxis="coloraxis"))

st.plotly_chart(fig_hist, use_container_width=True)


##TORNADOS PER SQ MILE
state_area = load_sq_mi()
grand_total = (tornado_filter.groupby(['st']).size()
                   .reset_index(name='Total Tornadoes')
                   .sort_values('Total Tornadoes', ascending=False))

state_agg = pd.merge(grand_total, state_area, on='st')
state_agg['tornadoes_per_sqmi'] = state_agg['Total Tornadoes'] / state_agg['square_miles']
fig_sq_mile = px.bar(state_agg.sort_values('tornadoes_per_sqmi', ascending=False), 
                     x='st', y='tornadoes_per_sqmi', 
                     color='Total Tornadoes', 
                     color_continuous_scale="Jet")
st.plotly_chart(fig_sq_mile, use_container_width=True)

##STATE INJ V FAT
state_data = tornado_filter.groupby('st').agg({'inj': 'sum', 'fat': 'sum'}).reset_index()
# Create the scatter plot
fig_scatter = px.scatter(state_data, x='inj', y='fat', color='st',
                 labels={'inj': 'Total Injuries', 'fat': 'Total Fatalities', 'st': 'State'},
                 title='Total Injuries vs Total Fatalities for each State')

fig_scatter.update_traces(marker=dict(size=30))

st.plotly_chart(fig_scatter, use_container_width=True)
import pandas as pd
import numpy as np
# SEABORN IS A PLOTTING LIBRARY
import seaborn as sns
# MATPLOT LIB IS ALSO A PLOTTING LIBRARY
import matplotlib.pyplot as plt
import streamlit as st
from flask import Flask, render_template
import dash 
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import json
import plotly.offline as pyo
import folium
import plotly.express as px
from folium.plugins import MarkerCluster
from statsmodels.api import qqplot
from dash import dash_table 
from dash import dcc
from dash.dependencies import Input, Output
import plotly.offline as py 
import plotly.graph_objs as go
import json
from datetime import datetime
df=pd.read_csv('MVC.csv')
def fill_null_zipcodes(input_df):  
    for index, row in input_df.iterrows():
        # Check if ZIPCODE is null
        if pd.isna(row['ZIP CODE']):
            # Retrieve zip code using reverse geocoding
            lat, lng = row['LATITUDE'], row['LONGITUDE']
            if pd.notna(lat) and pd.notna(lng):
                location = geolocator.reverse(f"{lat}, {lng}", exactly_one=True, language="en")
                if location.raw.get('address', {}).get('postcode'):
                    input_df.loc[:, 'ZIP CODE'] = input_df['ZIP CODE'].astype(str)
                    input_df.loc[index, 'ZIP CODE'] = location.raw['address']['postcode']
                    print(f"Filled ZIPCODE for row {index}: {location.raw['address']['postcode']}")
    return input_df
    
zip_code_data = df.groupby('ZIP CODE')['CONTRIBUTING FACTOR VEHICLE 1'].agg(lambda x: x.mode().iat[0]).reset_index()

# Load GeoJSON file
geojson_file = "zip_code_040114.geojson"
with open(geojson_file, 'r') as f:
    geojson_data = json.load(f)

# Merge your data with the GeoJSON file
merged_data = pd.merge(df, zip_code_data, on="ZIP CODE", how="left")

# Create an interactive choropleth map
fig = px.choropleth_mapbox(
    merged_data,
    geojson=geojson_data,
    featureidkey="properties.ZIPCODE",
    locations="ZIP CODE",
    color="CONTRIBUTING FACTOR VEHICLE 1_x",
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=9,
    center={"lat": 40.7, "lon": -73.9},
    opacity=0.7,
    hover_name="ZIP CODE",
    custom_data=['ZIP CODE', 'CONTRIBUTING FACTOR VEHICLE 1_x']
)
fig.update_traces(
    hovertemplate="<b>ZIP Code:</b> %{customdata[0]}<br>"
                   "<b>Most Common Factor:</b> %{customdata[1]}<extra></extra>"
)

fig.update_geos(fitbounds="locations", visible=False)  # Fit the map to the boundaries of the locations

df['CRASH TIME']=pd.to_datetime(df['CRASH TIME'])
df['Hour']=df['CRASH TIME'].dt.hour
import plotly.express as px

import plotly.express as px

hourly_fig = px.histogram(df, x='Hour', title='HOURLY Distribution of Car Crashes (2019-2022)',
                          labels={'Hour': 'HOUR OF THE DAY', 'count': 'Number of Crashes'},
                          nbins=24, color='Hour',
                          color_discrete_sequence=['blue'],
                          barnorm='fraction',  
                          barmode='overlay')

# Adjust the bargap to control the spacing between bars
hourly_fig.update_layout(showlegend=False)
hourly_fig.update_layout(bargap=0.2)



df['CRASH DATE']=pd.to_datetime(df['CRASH DATE'],format='%m/%d/%Y')
df['MONTH NAME']=df['CRASH DATE'].dt.strftime('%B')
alcohol_crashes = df[df['CONTRIBUTING FACTOR VEHICLE 1'] == 'Alcohol Involvement']

# Create a histogram for monthly alcohol-related crashes
monthly_alcohol_fig = px.histogram(alcohol_crashes, x='MONTH NAME', title='Monthly Distribution of Car Crashes due to Alcohol',
                                   labels={'MONTH NAME': 'MONTH', 'count': 'Number of Crashes'},
                                   color_discrete_sequence=['skyblue'])
st.title('Car Crash Analysis')

# Display the choropleth map
st.plotly_chart(fig)

# Display the hourly distribution histogram
st.plotly_chart(hourly_fig)

# Display the monthly alcohol-related crashes histogram
st.plotly_chart(monthly_alcohol_fig)
# Add this after the visualizations section
st.sidebar.title('Filter Data')

# Get user input for filtering
year = st.sidebar.number_input('Enter year', min_value=int(df['CRASH DATE'].dt.year.min()), max_value=int(df['CRASH DATE'].dt.year.max()))
month = st.sidebar.number_input('Enter month (1-12)', min_value=1, max_value=12)
zip_code = st.sidebar.text_input('Enter ZIP code')

# Add a button to trigger the analysis
if st.sidebar.button('Run Analysis'):
    # Run the analysis with the provided inputs
    filtered_data = df[(df['CRASH DATE'].dt.year == year) &
                       (df['CRASH DATE'].dt.month == month) &
                       (df['ZIP CODE'] == float(zip_code))]  # Convert ZIP code to float for comparison

    crashes_per_day = filtered_data['CRASH DATE'].dt.day.value_counts().sort_index()

    # Plot the bar chart
    st.pyplot(plt.figure(figsize=(10, 6)))
    plt.bar(crashes_per_day.index, crashes_per_day.values)
    plt.xlabel('Day of the Month')
    plt.ylabel('Number of Car Crashes')
    plt.title(f'Car Crashes in ZIP Code {zip_code} in {datetime(year, month, 1).strftime("%B %Y")}')
    st.pyplot(plt)


#Two Additional Visualizations:



    # Convert 'CRASH DATE' to datetime
df['CRASH DATE'] = pd.to_datetime(df['CRASH DATE'])

# Filter data for the year 2020
df_2020 = df[df['CRASH DATE'].dt.year == 2019]

# Create a new column 'Injury Severity' based on the number of persons injured
df_2020['Injury Severity'] = 'No Injury'  # Default to 'No Injury'
df_2020.loc[df_2020['NUMBER OF PERSONS INJURED'] > 0, 'Injury Severity'] = '1-2 Injuries'
df_2020.loc[df_2020['NUMBER OF PERSONS INJURED'] > 2, 'Injury Severity'] = '3-5 Injuries'
df_2020.loc[df_2020['NUMBER OF PERSONS INJURED'] > 5, 'Injury Severity'] = 'More than 5 Injuries'

# Calculate the count of accidents for each injury severity category
injury_counts_2020 = df_2020['Injury Severity'].value_counts().reset_index()
injury_counts_2020.columns = ['Injury Severity', 'Accident Count']

# Create a pie chart
fig = px.pie(injury_counts_2020, values='Accident Count', names='Injury Severity',
             title='Distribution of Injury Severity in Motor Vehicle Crashes in 2019',
             color_discrete_sequence=px.colors.diverging.PRGn)

# Display the pie chart using Streamlit
st.plotly_chart(fig)

# Assuming you have a DataFrame named 'df' with columns 'CRASH DATE', 'NUMBER OF PERSONS KILLED', and 'BOROUGH'
# Modify the column names as per your dataset

# Convert 'CRASH DATE' to datetime
df['CRASH DATE'] = pd.to_datetime(df['CRASH DATE'])

# Filter data for the year 2020 and fatal incidents
df_fatal_2020 = df[(df['CRASH DATE'].dt.year == 2019) & (df['NUMBER OF PERSONS KILLED'] > 0)]

# Create a new column 'Fatality Severity' based on the number of persons killed
df_fatal_2020['Fatality Severity'] = '1 Fatality'  # Default to '1 Fatality'
df_fatal_2020.loc[df_fatal_2020['NUMBER OF PERSONS KILLED'] > 1, 'Fatality Severity'] = '2 or More Fatalities'

# Calculate the count of accidents for each fatality severity category
fatality_counts_2020 = df_fatal_2020['Fatality Severity'].value_counts().reset_index()
fatality_counts_2020.columns = ['Fatality Severity', 'Accident Count']

# Create a pie chart
fig = px.pie(fatality_counts_2020, values='Accident Count', names='Fatality Severity',
             title='Distribution of Fatality Severity in Motor Vehicle Crashes in 2019',
             color_discrete_sequence=px.colors.diverging.PRGn)

# Display the pie chart using Streamlit
st.plotly_chart(fig)
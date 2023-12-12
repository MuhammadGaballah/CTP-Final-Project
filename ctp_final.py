
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import json
import zipfile
from datetime import datetime
import plotly.express as px
import json

with zipfile.ZipFile("newmvc.csv.zip", "r") as zip_ref:
   zip_ref.extract("newmvc.csv", "temp_folder")

with zipfile.ZipFile("MVC.csv.zip", "r") as zip_ref:
   zip_ref.extract("MVC.csv", "temp_folder")


df=pd.read_csv('temp_folder/newmvc.csv')
df2 = pd.read_csv('zip_code_data.csv', na_values='Unknown', encoding='utf-8')


#need the max
# Create an interactive choropleth map
geojson_file = "zip_code_040114.geojson"
with open(geojson_file, 'r') as f:
    geojson_data = json.load(f)
fig = px.choropleth_mapbox(
    df2,
    geojson=geojson_data,
    featureidkey="properties.ZIPCODE",
    locations="ZIP CODE",
    color="CONTRIBUTING FACTOR VEHICLE 1",
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=9,
    center={"lat": 40.7, "lon": -73.9},
    opacity=0.7,
    hover_name="ZIP CODE",
    custom_data=['ZIP CODE', 'CONTRIBUTING FACTOR VEHICLE 1']
)
fig.update_traces(
    hovertemplate="<b>ZIP Code:</b> %{customdata[0]}<br>"
                   "<b>Most Common Factor:</b> %{customdata[1]}<extra></extra>"
)

fig.update_geos(fitbounds="locations", visible=False)  # Fit the map to the boundaries of the locations

df['CRASH TIME']=pd.to_datetime(df['CRASH TIME'])
df['Hour']=df['CRASH TIME'].dt.hour
df['CRASH DATE'] = pd.to_datetime(df['CRASH DATE'], format="%Y-%m-%d")
hourly_fig = px.histogram(df, x='Hour', title='HOURLY Distribution of Car Crashes (2019-2022)',
                          labels={'Hour': 'HOUR OF THE DAY', 'count': 'Number of Crashes'},
                          nbins=24, color='Hour',
                          color_discrete_sequence=['blue'],
                          barnorm='fraction',  
                          barmode='overlay')

# Adjust the bargap to control the spacing between bars
hourly_fig.update_layout(showlegend=False)
hourly_fig.update_layout(bargap=0.2)
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
st.plotly_chart(monthly_alcohol_fig)
# Display the monthly alcohol-related crashes histogram
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
# Create a pie chart

# Display the pie chart 
#Two Additional Visualizations:
df3=pd.read_csv('temp_folder/MVC.csv')


    # Convert 'CRASH DATE' to datetime
df3['CRASH DATE'] = pd.to_datetime(df3['CRASH DATE'])

# Filter data for the year 2020
df_2020 = df3[df3['CRASH DATE'].dt.year == 2019]

# Create a new column 'Injury Severity' based on the number of persons injured
df_2020['Injury Severity'] = 'No Injury'  # Default to 'No Injury'
df_2020.loc[df_2020['NUMBER OF PERSONS INJURED'] > 0, 'Injury Severity'] = '1-2 Injuries'
df_2020.loc[df_2020['NUMBER OF PERSONS INJURED'] > 2, 'Injury Severity'] = '3-5 Injuries'
df_2020.loc[df_2020['NUMBER OF PERSONS INJURED'] > 5, 'Injury Severity'] = 'More than 5 Injuries'

# Calculate the count of accidents for each injury severity category
injury_counts_2020 = df_2020['Injury Severity'].value_counts().reset_index()
injury_counts_2020.columns = ['Injury Severity', 'Accident Count']

# Create a pie chart
injury = px.pie(injury_counts_2020, values='Accident Count', names='Injury Severity',
             title='Distribution of Injury Severity in Motor Vehicle Crashes in 2019',
             color_discrete_sequence=px.colors.diverging.PRGn)

# Display the pie chart using Streamlit
st.plotly_chart(injury)


# Filter data for the year 2020 and fatal incidents
df_fatal_2020 = df3[(df3['CRASH DATE'].dt.year == 2019) & (df3['NUMBER OF PERSONS KILLED'] > 0)]

# Create a new column 'Fatality Severity' based on the number of persons killed
df_fatal_2020['Fatality Severity'] = '1 Fatality'  # Default to '1 Fatality'
df_fatal_2020.loc[df_fatal_2020['NUMBER OF PERSONS KILLED'] > 1, 'Fatality Severity'] = '2 or More Fatalities'

# Calculate the count of accidents for each fatality severity category
fatality_counts_2020 = df_fatal_2020['Fatality Severity'].value_counts().reset_index()
fatality_counts_2020.columns = ['Fatality Severity', 'Accident Count']

# Create a pie chart
fatility = px.pie(fatality_counts_2020, values='Accident Count', names='Fatality Severity',
             title='Distribution of Fatality Severity in Motor Vehicle Crashes in 2019',
             color_discrete_sequence=px.colors.diverging.PRGn)

# Display the pie chart using Streamlit
st.plotly_chart(fatility)

df_filtered = df[(df['CRASH DATE'].dt.year >= 2018) & (df['CRASH DATE'].dt.year <= 2022)]

# Group data by year and count the number of crashes in each year
crashes_by_year = df_filtered['CRASH DATE'].dt.year.value_counts().sort_index()

# Streamlit app
st.title('Car Crash Analysis')
st.subheader('Trend of Total Car Crashes (2018-2022)')

# Plot using matplotlib in Streamlit
fig_year, ax = plt.subplots(figsize=(12, 6))
ax.plot(crashes_by_year.index, crashes_by_year.values, marker='o', linestyle='-')
ax.set(xlabel='Year', ylabel='Number of Car Crashes', title='Trend of Total Car Crashes (2018-2022)')
ax.grid(True)

# Show the plot in Streamlit
st.pyplot(fig_year)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import math

plt.rcParams["font.family"] = "tahoma"

# Read data
df = pd.read_csv("RainDaily_Tabular.csv")
df["date"] = pd.to_datetime(df["date"])

# Sidebar
st.sidebar.title("Filter")
provinceList = sorted(df["province"].unique().tolist())
province = st.sidebar.selectbox("Province", provinceList)
dateList = df["date"].dt.date.unique().tolist()
date = st.sidebar.selectbox("Date", dateList)

# Main

st.title("Rain Data Analysis")

st.write(f"Province: {province}")
st.write(f"Date: {date}")

# Line chart for rain by date
st.subheader(f"Line Chart for Average Rain in {province} by Date")
fig, ax = plt.subplots()
fig.set_size_inches(10, 5)
data = df[df["province"] == province]
# split data by "code" and plot a line for each code
codes = data["code"].unique()
for code in codes:
    code_data = data[data["code"] == code]
    ax.plot(code_data["date"], code_data["rain"], label=code)
ax.legend(title="Code", bbox_to_anchor=(1, 1))
ax.set_xlabel("Date")
ax.set_ylabel(f"Average Rain in {province}")
st.pyplot(fig)

# Analyze Rain Data in term of area and time
st.subheader(f"Analyze Rain Data in {province}")
# select data for the selected province
data = df[df["province"] == province]
data = data[data["date"].dt.date == date]

# write a description
st.write(f"Total Rain: {data['rain'].sum()}")
st.write(f"Average Rain: {math.floor(data['rain'].mean() * 1e2)/1e2}")
st.write(
    f"Max Rain: {data['rain'].max()} at {data['name'][data['rain'].idxmax()]} in {data['amphoe'][data['rain'].idxmax()]}"
)
st.write(
    f"Min Rain: {data['rain'].min()} at {data['name'][data['rain'].idxmin()]} in {data['amphoe'][data['rain'].idxmin()]}"
)

# get data only code and name columns
code_data = data.drop(
    columns=["date", "latitude", "longitude", "rain", "datetime"]
).reset_index(drop=True)
st.subheader("Code and Location")
st.write(code_data)

# Bar chart for rain by code
st.subheader("Bar Chart for Rain by Code")
fig, ax = plt.subplots()
fig.set_size_inches(10, 5)
rain_by_code = data.groupby("code")["rain"].mean().sort_values()
codes = rain_by_code.index
ax.barh(codes, rain_by_code)
ax.set_xlabel("Code")
ax.set_ylabel("Rain")
st.pyplot(fig)

# Map for rain by location
st.subheader("Map for Rain by Location")
# filter data only for the selected date
data = df[df["date"].dt.date == date]
view = pdk.ViewState(
    latitude=data["latitude"].mean(),
    longitude=data["longitude"].mean(),
    zoom=5,
    pitch=0,
)
data["normalized_rain"] = data["rain"].apply(lambda x: math.sqrt(x))
data["normalized_rain"] = data["normalized_rain"] / data["normalized_rain"].max()
layer = pdk.Layer(
    "ScatterplotLayer",
    data,
    get_position=["longitude", "latitude"],
    get_radius=10000,
    get_fill_color="[2, 204, 254, normalized_rain * 255]",
    pickable=True,
)
tooltip = {"html": "<b>Location:</b> {name}<br><b>Rain:</b> {rain}"}
st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v9",
        initial_view_state=view,
        layers=[layer],
        tooltip=tooltip,
    )
)

# Overall Rain Data
st.header("Overall Rain Data")
# Bar chart for average rain by province
st.subheader("Bar Chart for Average Rain by Province")
fig, ax = plt.subplots()
fig.set_size_inches(5, 20)
provinces_avg_rain = df.groupby("province")["rain"].mean()
# sort data by average rain
provinces_avg_rain = provinces_avg_rain.sort_values()
ax.barh(provinces_avg_rain.index, provinces_avg_rain)
ax.set_xlabel("Average Rain")
ax.set_ylabel("Province")
st.pyplot(fig)

# Line chart for rain by date
st.subheader("Line Chart for Average Rain by Date")
fig, ax = plt.subplots()
fig.set_size_inches(10, 5)
data = df
dates = data["date"].unique()
rain_by_date = df.groupby("date")["rain"].mean()
ax.plot(dates, rain_by_date)
ax.set_xlabel("Date")
ax.set_ylabel("Average Rain")
st.pyplot(fig)

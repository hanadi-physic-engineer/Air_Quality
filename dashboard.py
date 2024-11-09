import pandas as pd
import plotly.colors as PC
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Judul aplikasi
st.title("Air Quality Data Analysis")
urls = [
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Aotizhongxin_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Changping_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Dingling_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Dongsi_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Guanyuan_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Gucheng_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Huairou_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Nongzhanguan_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Shunyi_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Tiantan_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Wanliu_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Wanshouxigong_20130301-20170228.csv'
]

@st.cache_data
def load_data(urls):
    data_frames = [pd.read_csv(url, on_bad_lines='skip') for url in urls]
    data = pd.concat(data_frames, ignore_index=True)
    return data

data = load_data(urls)

data['datetime'] = pd.to_datetime(data[['year', 'month', 'day', 'hour']])
def categorize_air_quality(pm25_value):
    if pm25_value <= 50:
        return "Good"
    elif pm25_value <= 100:
        return "Moderate"
    elif pm25_value <= 150:
        return "Unhealthy for Sensitive Groups"
    elif pm25_value <= 200:
        return "Unhealthy"
    elif pm25_value <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

data['Category'] = data['PM2.5'].apply(categorize_air_quality)

# Sidebar: Filter data
st.sidebar.header('Filter Data')
year = st.sidebar.multiselect('Select Year', options=data['year'].unique(), default=data['year'].unique())
month = st.sidebar.slider('Select Month', 1, 12, (1, 12))
hour_range = st.sidebar.slider('Select Hour Range', 0, 23, (0, 23))

filtered_data = data[(data['year'].isin(year)) & 
                     (data['month'] >= month[0]) & 
                     (data['month'] <= month[1]) &
                     (data['hour'] >= hour_range[0]) & 
                     (data['hour'] <= hour_range[1])]

st.subheader("Data Sample")
st.write(filtered_data.head())

st.subheader("Air Quality Category Counts per Station")
station_category_counts = filtered_data.groupby(['station', 'Category']).size().unstack(fill_value=0)
fig_station_bar = go.Figure()

for category in station_category_counts.columns:
    fig_station_bar.add_trace(
        go.Bar(
            x=station_category_counts.index,
            y=station_category_counts[category],
            name=category
        )
    )

fig_station_bar.update_layout(
    barmode='stack',
    title="Air Quality Category Counts per Station",
    xaxis_title="Station",
    yaxis_title="Count"
)
st.plotly_chart(fig_station_bar)

st.subheader("Correlation Heatmap")
corr_matrix = filtered_data.corr(numeric_only=True)
fig_heatmap = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns,
    y=corr_matrix.columns,
    colorscale='RdBu',
    zmin=-1, zmax=1
))
fig_heatmap.update_layout(title="Correlation Heatmap")
st.plotly_chart(fig_heatmap)

st.subheader("Distributions of Air Quality Parameters Over Time")
parameters = ['PM2.5', 'PM10', 'TEMP', 'PRES', 'DEWP', 'RAIN']
fig_param_grid = make_subplots(rows=3, cols=2, subplot_titles=parameters)

for i, parameter in enumerate(parameters):
    row = i // 2 + 1
    col = i % 2 + 1
    monthly_avg = filtered_data.groupby([filtered_data['datetime'].dt.to_period("M"), 'station'])[parameter].mean().unstack()
    for station in monthly_avg.columns:
        fig_param_grid.add_trace(
            go.Scatter(x=monthly_avg.index.to_timestamp(), y=monthly_avg[station], mode='lines', name=station),
            row=row, col=col
        )
    fig_param_grid.update_xaxes(title_text="Month", row=row, col=col)
    fig_param_grid.update_yaxes(title_text=parameter, row=row, col=col)

fig_param_grid.update_layout(title="Distributions of Air Quality Parameters Over Time", showlegend=True)
st.plotly_chart(fig_param_grid)

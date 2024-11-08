import pandas as pd
import plotly.colors as PC
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st

# Judul aplikasi
st.title("Air Quality Data Analysis")
# Daftar URL file CSV dari GitHub (gunakan link "raw" yang benar)
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

# Fungsi untuk memuat dataset
@st.cache_data
def load_data(urls):
    # Memuat setiap URL dan menggabungkan menjadi satu DataFrame
    data_frames = [pd.read_csv(url, on_bad_lines='skip') for url in urls]
    data = pd.concat(data_frames, ignore_index=True)
    return data
# Memuat data dengan memberikan parameter `urls` ke fungsi load_data
data = load_data(urls)



# Buat kolom `datetime` dari kolom `year`, `month`, `date`, dan `hour`
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

# Tambahkan kolom Category
data['Category'] = data['PM2.5'].apply(categorize_air_quality)

# Sidebar: Filter data
st.sidebar.header('Filter Data')
year = st.sidebar.multiselect('Select Year', options=data['year'].unique(), default=data['year'].unique())
month = st.sidebar.slider('Select Month', 1, 12, (1, 12))
hour_range = st.sidebar.slider('Select Hour Range', 0, 23, (0, 23))

# Filter data berdasarkan pilihan di sidebar
filtered_data = data[(data['year'].isin(year)) & 
                     (data['month'] >= month[0]) & 
                     (data['month'] <= month[1]) &
                     (data['hour'] >= hour_range[0]) & 
                     (data['hour'] <= hour_range[1])]

# Tampilkan data
st.subheader("Data Sample")
st.write(filtered_data.head())

# Tampilkan informasi dataset
st.subheader("Dataset Info")
st.text(filtered_data.info())

# Tampilkan deskripsi statistik
st.subheader("Statistical Description")
st.write(filtered_data.describe())

# Define custom category order for air quality
custom_category_order = [
    "Good", "Moderate", "Unhealthy for Sensitive Groups",
    "Unhealthy", "Very Unhealthy", "Hazardous"
]

# Filter untuk kategori kualitas udara
st.sidebar.subheader("Air Quality Category Filter")
selected_category = st.sidebar.selectbox('Select Category', ["Overall"] + custom_category_order)

if selected_category != "Overall":
    filtered_data = filtered_data[filtered_data['Category'] == selected_category]

# Analisis Frekuensi Kategori Kualitas Udara
st.subheader("Air Quality Category Frequency")
category_counts = filtered_data['Category'].value_counts().reindex(custom_category_order, fill_value=0)
fig_category = px.bar(category_counts, x=category_counts.index, y=category_counts.values,
                      labels={'x': 'Air Quality Category', 'y': 'Frequency'},
                      title="Air Quality Category Distribution")
st.plotly_chart(fig_category)

# Analisis Distribusi PM2.5
st.subheader("PM2.5 Distribution")
fig_pm25 = px.histogram(filtered_data, x='PM2.5', nbins=50,
                        title="PM2.5 Concentration Distribution")
st.plotly_chart(fig_pm25)

# Grafik Garis PM2.5 Berdasarkan Waktu
st.subheader("PM2.5 Levels Over Time")
fig_pm25_time = px.line(filtered_data, x='datetime', y='PM2.5',
                        title="PM2.5 Levels Over Time")
st.plotly_chart(fig_pm25_time)

# Analisis Korelasi Antara Parameter Cuaca dan PM2.5
st.subheader("Correlation Between Weather Parameters and PM2.5")
weather_parameters = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'wd', 'WSPM']
param1 = st.selectbox('Select Weather Parameter 1', weather_parameters, index=0)
param2 = st.selectbox('Select Weather Parameter 2', weather_parameters, index=1)

fig_scatter = px.scatter(filtered_data, x=param1, y=param2, color='Category',
                         title=f"{param1} vs {param2} by Air Quality Category")
st.plotly_chart(fig_scatter)

# Visualisasi Polar Berdasarkan Arah Angin dan Kategori
st.subheader("Wind Direction and Air Quality Category")
wind_categories = filtered_data.groupby(['wd', 'Category']).size().reset_index(name='count')
wind_categories['Category'] = pd.Categorical(wind_categories['Category'], categories=custom_category_order, ordered=True)
wind_categories = wind_categories.sort_values(by=['Category', 'wd'])

fig_polar = go.Figure()

for category in custom_category_order:
    category_data = wind_categories[wind_categories['Category'] == category]
    fig_polar.add_trace(go.Barpolar(
        r=category_data['count'],
        theta=category_data['wd'],
        name=category,
        marker=dict(color=PC.qualitative.Set1[custom_category_order.index(category)])
    ))

fig_polar.update_layout(
    title="Wind Direction Distribution by Air Quality Category",
    polar=dict(radialaxis=dict(visible=True)),
    barmode="stack"
)
st.plotly_chart(fig_polar)
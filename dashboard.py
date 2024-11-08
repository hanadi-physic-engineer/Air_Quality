import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import streamlit as st

# Judul aplikasi
st.title("Air Quality Data Analysis")

# Daftar URL file CSV dari GitHub (gunakan link "raw" yang benar)
urls = [
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Aotizhongxin_20130301-20170228.csv',
    'https://raw.githubusercontent.com/hanadi-physic-engineer/Air_Quality/main/PRSA_Data_Changping_20130301-20170228.csv',
    # ... Tambahkan URL lainnya seperti sebelumnya ...
]

# Fungsi untuk memuat dataset
@st.cache_data
def load_data(urls):
    # Memuat setiap URL dan menggabungkan menjadi satu DataFrame
    data_frames = [pd.read_csv(url, on_bad_lines='skip') for url in urls]
    data = pd.concat(data_frames, ignore_index=True)
    return data

# Memuat data
data = load_data(urls)

# Buat kolom `datetime` dari kolom `year`, `month`, `day`, dan `hour`
data['datetime'] = pd.to_datetime(data[['year', 'month', 'day', 'hour']])

# Fungsi untuk kategorisasi kualitas udara
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
buffer = io.StringIO()
filtered_data.info(buf=buffer)
s = buffer.getvalue()
st.text(s)

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

# Visualisasi Frekuensi Kategori Kualitas Udara
st.subheader("Air Quality Category Frequency")
plt.figure(figsize=(10, 6))
sns.countplot(data=filtered_data, x='Category', order=custom_category_order)
plt.title("Air Quality Category Distribution")
plt.xlabel("Air Quality Category")
plt.ylabel("Frequency")
st.pyplot(plt)

# Distribusi PM2.5
st.subheader("PM2.5 Distribution")
plt.figure(figsize=(10, 6))
sns.histplot(filtered_data['PM2.5'], bins=50, kde=True)
plt.title("PM2.5 Concentration Distribution")
plt.xlabel("PM2.5 Concentration")
plt.ylabel("Frequency")
st.pyplot(plt)

# Grafik Garis PM2.5 Berdasarkan Waktu
st.subheader("PM2.5 Levels Over Time")
plt.figure(figsize=(10, 6))
sns.lineplot(data=filtered_data, x='datetime', y='PM2.5')
plt.title("PM2.5 Levels Over Time")
plt.xlabel("Date Time")
plt.ylabel("PM2.5")
st.pyplot(plt)

# Analisis Korelasi Antara Parameter Cuaca dan PM2.5
st.subheader("Correlation Between Weather Parameters and PM2.5")
weather_parameters = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'wd', 'WSPM']
param1 = st.selectbox('Select Weather Parameter 1', weather_parameters, index=0)
param2 = st.selectbox('Select Weather Parameter 2', weather_parameters, index=1)

plt.figure(figsize=(10, 6))
sns.scatterplot(data=filtered_data, x=param1, y=param2, hue='Category', palette="Set1")
plt.title(f"{param1} vs {param2} by Air Quality Category")
plt.xlabel(param1)
plt.ylabel(param2)
st.pyplot(plt)

# Distribusi Berdasarkan Arah Angin
st.subheader("Wind Direction and Air Quality Category")
wind_categories = filtered_data.groupby(['wd', 'Category']).size().unstack(fill_value=0)
wind_categories.plot(kind='bar', stacked=True, colormap="Set1", figsize=(10, 6))
plt.title("Wind Direction Distribution by Air Quality Category")
plt.xlabel("Wind Direction")
plt.ylabel("Frequency")
st.pyplot(plt)

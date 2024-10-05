import pandas as pd
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns
import streamlit as st
sns.set(style='dark')

day_df = pd.read_csv('clean_day_df.csv')  
hour_df= pd.read_csv('clean_hour_df.csv')

def create_byseason_avg_df (df):
    season_avg_df = df.groupby('Musim')['Total_Pengguna'].mean().reset_index()
    return season_avg_df

def create_byweektype_avg_df (df):
    weektype_avg_df = df.groupby('Jenis_Hari')['Total_Pengguna'].mean().reset_index()
    return weektype_avg_df

def classify_rush_hour(hour):
    if 6 <= hour < 9:  
        return 'Jam Ramai Pagi'
    elif 16 <= hour < 19:  
        return 'Jam Ramai Sore'
    else:
        return 'Jam Biasa'

day_df['Tanggal'] = pd.to_datetime(day_df['Tanggal'])
min_date = day_df['Tanggal'].min()
max_date = day_df['Tanggal'].max()

with st.sidebar:
    st.image("https://cdn.vectorstock.com/i/1000x1000/21/31/logo-for-bicycle-rental-vector-25512131.webp", caption="Bike Rentals")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_day_df = day_df[(day_df['Tanggal'] >= str(start_date)) & 
                 (day_df['Tanggal'] <= str(end_date))]

main_hour_df = hour_df[(hour_df['Tanggal'] >= str(start_date)) &
                    (hour_df['Tanggal'] <= str(end_date))]

season_avg_df = create_byseason_avg_df(main_day_df)
byweektype_avg_df = create_byweektype_avg_df(main_day_df)

st.header('Bike Rental Company')
st.subheader('Distribusi Penyewaan Sepeda per Hari')

fig, ax = plt.subplots()
sns.histplot(main_day_df['Total_Pengguna'], bins=30, kde=True, ax=ax)
ax.set_xlabel('Jumlah Rental Sepeda')
ax.set_ylabel('Frekuensi')
st.pyplot(fig)

col1, col2, col3 = st.columns(3)

with col1:
    total_casual_users = main_day_df['Pengguna_Umum'].sum()
    st.metric("Pengguna Umum: ", value = total_casual_users)

with col2:
    total_registered_users = main_day_df['Pengguna_Terdaftar'].sum()
    st.metric("Pengguna Terdaftar", value = total_registered_users)

with col3:
    total_users = main_day_df['Total_Pengguna'].sum()
    st.metric("Total Penyewa", value = total_users)

st.subheader('Rata-Rata Jumlah Penyewa Per Hari Berdasarkan Musim')

max_value = season_avg_df['Total_Pengguna'].max()

fig, ax = plt.subplots()
colors = ['red' if val == max_value else 'lightgray' for val in season_avg_df['Total_Pengguna']]
sns.barplot(x = 'Musim', y = 'Total_Pengguna', data = season_avg_df, ax = ax, palette=colors)
ax.set_xlabel('Musim')
ax.set_ylabel('Rata-Rata Jumlah Rental')

for index, value in enumerate(season_avg_df['Total_Pengguna']):
    ax.text(index, value + 10, str(round(int(value), 0)), ha='center') 

st.pyplot(fig)

st.subheader('Rata-Rata Sewa Sepeda: Hari Kerja vs Akhir Pekan/Libur')

max_value = byweektype_avg_df['Total_Pengguna'].max()

fig, ax = plt.subplots()
colors = ['red' if val == max_value else 'lightgray' for val in byweektype_avg_df['Total_Pengguna']]
sns.barplot(x = 'Jenis_Hari', y = 'Total_Pengguna', data = byweektype_avg_df, ax =ax, palette= colors)
ax.set_xlabel('Jenis Hari')
ax.set_ylabel('Rata-Rata Sewa Sepeda')

for index, value in enumerate(byweektype_avg_df['Total_Pengguna']):
    ax.text(index, value + 10, str(round(int(value), 0)), ha='center') 

st.pyplot(fig)

st.subheader('Rata-Rata Sewa Sepeda: Jam Ramai vs Jam Biasa')

main_hour_df['Kelas_Jam'] = main_hour_df['Jam'].apply(classify_rush_hour)

hari_kerja = main_hour_df[main_hour_df['Jenis_Hari'] == 'Hari Kerja']

kelasjam = hari_kerja.groupby(['Kelas_Jam','Jam'])['Total_Pengguna'].mean().unstack('Kelas_Jam').sort_values(by='Jam', ascending = False)

fig = plt.figure()
ax = kelasjam.plot(kind='barh', stacked=True, color=['grey', 'black', 'black'], ax=fig.gca())

plt.xlabel('Rata-Rata Jumlah Sewa')
plt.ylabel('Jam')

for container in ax.containers:
    ax.bar_label(
        container,
        label_type='edge',
        fmt='%4.0f',
        labels=[f'{v:.0f}' if v > 0 else '' for v in container.datavalues],
        fontsize=7
    )

st.pyplot(fig)


st.subheader('Kondisi Cuaca vs Jumlah Penyewa')
akhir_pekan_libur = main_day_df[main_day_df['Jenis_Hari'] == 'Akhir Pekan/Libur']

plt.figure(figsize=(14, 10))
# Plot 1: Suhu vs Penyewaan Sepeda
plt.subplot(3, 1, 1)
sns.scatterplot(x='Suhu_(Celcius)', y='Total_Pengguna', data=akhir_pekan_libur)
plt.title('Suhu vs Jumlah Sewa Sepeda pada Akhir Pekan/Libur')
plt.xlabel('Suhu (Ternormalisasi)')
plt.ylabel('Jumlah Sewa Sepeda')

# Plot 2: Kelembaban vs Penyewaan Sepeda
plt.subplot(3, 1, 2)
sns.scatterplot(x='Kelembapan', y='Total_Pengguna', data=akhir_pekan_libur)
plt.title('Kelembapan vs Jumlah Sewa Sepeda pada Akhir Pekan/Libur')
plt.xlabel('Kelembapan (Ternormalisasi)')
plt.ylabel('Jumlah Sewa Sepeda')

# Plot 3: Kecepatan Angin vs Penyewaan Sepeda
plt.subplot(3, 1, 3)
sns.scatterplot(x='Kecepatan_Angin', y='Total_Pengguna', data=akhir_pekan_libur)
plt.title('Kecepatan Angin vs Jumlah Sewa Sepeda pada Akhir Pekan/Libur')
plt.xlabel('Kecepatan Angin (Ternormalisasi)')
plt.ylabel('Jumlah Sewa Sepeda')

plt.tight_layout()
st.pyplot(plt.gcf()) 

# Korelasi dan heatmap
correlation = akhir_pekan_libur[['Suhu_(Celcius)', 'Kelembapan', 'Kecepatan_Angin', 'Total_Pengguna']].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation, annot=True, cmap='coolwarm', linewidths=0.5, fmt='.2f')
plt.title('Korelasi antara Variabel Cuaca dan Jumlah Sewa Sepeda')

st.pyplot(plt.gcf())  

st.caption('Copyright (c) Timmothy Farrel 2024 ')

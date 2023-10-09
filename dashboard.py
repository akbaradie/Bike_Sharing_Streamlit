import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime
from babel.numbers import format_currency
sns.set(style='dark')


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "instant": "nunique",
        "cnt": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "total_price": "revenue"
    }, inplace=True)

    return daily_orders_df

def create_daily_comparation_df(df):
    daily_comparation_df = df.resample(rule='D', on='dteday').agg({
        "instant": "nunique",
        "casual": "sum",
        "registered": "sum"
    })
    daily_comparation_df = daily_comparation_df.reset_index()
    daily_comparation_df.rename(columns={
        "casual": "Casual",
        "registered": "Registered"
    }, inplace=True)
    return daily_comparation_df

def create_bystate_df(df):
    hari_dict = {0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'}
    bystate_df = df.groupby(by='weekday',as_index=False).cnt.sum()
    bystate_df = bystate_df.replace({"weekday":hari_dict})
    return bystate_df

day_df = pd.read_csv("main_data.csv")

day_df['dteday'] = pd.to_datetime(day_df['dteday'])
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_df[(day_df["dteday"] >= str(start_date)) &
                (day_df["dteday"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
daily_comparation_df = create_daily_comparation_df(main_df)
bystate_df = create_bystate_df(main_df)

st.header('Bike Sharing Dashboard')

#Line Plot
st.subheader('Peminjaman Sepeda Setiap Hari')
col1, col2 = st.columns(2)

with col1:
    total_peminjam = daily_orders_df.cnt.sum()
    st.metric("Total Peminjaman Sepeda", value=total_peminjam,delta=int(daily_orders_df.cnt.values[-1]-daily_orders_df.cnt.values[-2]))

with col2:
    rentang_waktu = daily_orders_df.instant.sum()
    st.metric("Rentang Waktu", value=str(rentang_waktu)+' Hari')

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["dteday"],
    daily_orders_df["cnt"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Demografi Peminjam Sepeda")
#Pie Chart
col1, col2 = st.columns(2)
with col1:
    casual_cust = daily_comparation_df.Casual.sum()
    st.metric("Peminjam Casual", value=casual_cust)

with col2:
    registered_cust = daily_comparation_df.Registered.sum()
    st.metric("Peminjam Registered", value=registered_cust)

fig, ax = plt.subplots(figsize=(10, 10))
explode = (0,0.1)
ax.pie([casual_cust,registered_cust],
       explode=explode,
        labels=["Casual","Registered"],
       autopct='%1.1f%%',
       textprops={'fontsize': 30},
       colors=sns.color_palette('bright'))
plt.title("Perbandingan Peminjam Oleh Casual VS Registered",fontsize=30)
st.pyplot(fig)

st.subheader("Peminjam Sepeda Terbanyak & Tersedikit Berdasarkan Hari")
bystate_df = bystate_df.sort_values(by="cnt", ascending=False)
col1, col2 = st.columns(2)
with col1:
    st.metric("Peminjam Terbanyak", value=int(bystate_df['cnt'].values[0]))

with col2:
    st.metric("Peminjam Tersedikit", value=int(bystate_df['cnt'].values[-1]))

#Horizontal Bar Chart
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#90CAF9"]
colors[len(bystate_df["weekday"])-1]="#90CAF9"
sns.barplot(
    x="cnt",
    y="weekday",
    data=bystate_df.sort_values(by="cnt", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Total Peminjaman Sepeda Berdasarkan Hari", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

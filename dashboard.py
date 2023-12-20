import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import streamlit as st 
from babel.numbers import format_currency
sns.set(style='dark')


# create_daily_orders_df() untuk menyiapkan daily_orders_df
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

# create_sum_order_items_df() untuk menyiapkan sum_orders_item_df
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").freight_value.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# create_bystate_df() untuk menyiapkan bystate_df
def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

# selanjutnya load berkas all_data.csv sebagai DataFrame
all_df = pd.read_csv("all_data.csv")


# mengurutkan DataFrame berdasarkan order_purchase_timestamp serta memastikan kedua kolom tersebut bertipe datetime.#

datetime_columns = ["order_purchase_timestamp", "order_approved_at"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
# MEMBUAT KOMPONEN FILTER
# menggunakan wedget date input sebagai filtering dan disimpan dibagian sidebar. dan menambahkan logo perusahaan

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("shop.png", use_column_width=True)
    
    # Tambahkan spasi untuk memusatkan gambar
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
# nantinya kode diatas akan menghasilkan start_date dan end_date yang akan dijadikan filtering dataframe.

# data yang sudah difilter akan disimpan kedalam main_df
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# dataframe yg telah difilter (main_df) yang dgunakan utk menghasilkan berbagai dataframe yang dibtuuhkan untuk membuat visualisasi data. proses ini dilakukan dengan memanggil helper function yang sudah dibuat sebelumnya.

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)


# MELENGKAPI DASHBOARD DENGAN BERBAGAI VISUALISASI DATA
# menambahkan header pada dashboard

st.header('E-Commerce Public :sparkles:')

# menambahkan informasi daily orders pada dashboard

# 1. Menampilkan informasi total order dan revenue dalam bentuk metric() yang ditampilkan dengan layout coloumns()
# 2. menampilkan jumlah order harian dengan bentuk visualisasi data.

st.subheader('Performa Penjualan Harian')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# menyertakan informasi performa penjualan setiap produk
# menampilkan 5 produk paling laris dan paling sedikit terjual

st.subheader("Performa Penjualan Produk")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="freight_value", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Berdasarkan Penjualan", fontsize=30)
ax[0].set_title("Produk Laris Terjual", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="freight_value", y="product_category_name", data=sum_order_items_df.sort_values(by="freight_value", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Berdasarkan Penjualan", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk Sedikit Terjual", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

# menampilkan demografi pelanggan yang dimiliki.
st.subheader("Demografis Pelanggan")
 
col1, col2 = st.columns(2)
 
with col1:
 
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="customer_count", 
        y="customer_state",
        data=bystate_df.sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax
)
ax.set_title("Jumlah Pelanggan Berdasarkan State", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.caption('Copyright (c) E-Commerce Public 2023')

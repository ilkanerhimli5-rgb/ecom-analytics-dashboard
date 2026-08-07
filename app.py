import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="E-Ticarət Data və Trend Analitikası",
    page_icon="📊",
    layout="wide"
)

st.title("📊 E-Ticarət Qiymət və Satış Analitikası")
st.markdown("Öz Excel/CSV faylınızı yükləyin və ya hazır nümunə məlumatları ilə analiz edin.")

# SIDEBAR: Fayl yükləmə hissəsi
st.sidebar.header("📁 Data Daxil Etmə")
uploaded_file = st.sidebar.file_uploader(
    "Excel və ya CSV faylı yükləyin", 
    type=["xlsx", "xls", "csv"]
)

@st.cache_data
def load_default_data():
    np.random.seed(42)
    dates = pd.date_range(start="2026-07-01", periods=30, freq="D")
    products = ["Wireless Earbuds X", "Smart Fitness Watch", "Ergonomic Desk Chair", "Portable Power Bank"]
    
    records = []
    base_prices = {"Wireless Earbuds X": 45, "Smart Fitness Watch": 120, "Ergonomic Desk Chair": 210, "Portable Power Bank": 35}
    base_costs = {"Wireless Earbuds X": 22, "Smart Fitness Watch": 65, "Ergonomic Desk Chair": 110, "Portable Power Bank": 15}
    categories = {"Wireless Earbuds X": "Elektronika", "Smart Fitness Watch": "Elektronika", "Ergonomic Desk Chair": "Ofis Mebeli", "Portable Power Bank": "Aksessuarlar"}

    for d in dates:
        for p in products:
            price = base_prices[p] + np.random.randint(-4, 7)
            sales = np.random.randint(15, 85)
            cost = base_costs[p]
            records.append({
                "Tarix": d.strftime("%Y-%m-%d"),
                "Məhsul": p,
                "Kateqoriya": categories[p],
                "Qiymət ($)": price,
                "Maya Dəyəri ($)": cost,
                "Günlük Satış": sales
            })
    return pd.DataFrame(records)

def auto_map_columns(df):
    """Excel faylındakı sütun adlarını avtomatik tanıyır və uyğunlaşdırır"""
    mapping = {}
    for col in df.columns:
        c_lower = str(col).strip().lower()
        if any(k in c_lower for k in ["tarix", "date", "gün", "gun"]):
            mapping[col] = "Tarix"
        elif any(k in c_lower for k in ["məhsul", "mahsul", "product", "item", "ad", "name"]):
            mapping[col] = "Məhsul"
        elif any(k in c_lower for k in ["qiymət", "qiymet", "price", "dəyər", "deyer", "düyər"]):
            mapping[col] = "Qiymət ($)"
        elif any(k in c_lower for k in ["satış", "satis", "sales", "miqdar", "ədəd", "eded", "qty", "quantity"]):
            mapping[col] = "Günlük Satış"
        elif any(k in c_lower for k in ["maya", "xərc", "xerc", "cost"]):
            mapping[col] = "Maya Dəyəri ($)"
    return df.rename(columns=mapping)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        df = auto_map_columns(df)
        st.sidebar.success("✅ Fayl uğurla yükləndi!")
    except Exception as e:
        st.sidebar.error(f"⚠️ Fayl oxunarkən xəta baş verdi: {e}")
        st.error(f"Fayl oxunmasında texniki xəta: {e}")
        df = load_default_data()
else:
    st.sidebar.info("💡 Nümunə məlumatlardan istifadə olunur.")
    df = load_default_data()

required_cols = ["Tarix", "Məhsul", "Qiymət ($)", "Günlük Satış"]
has_required = all(col in df.columns for col in required_cols)

if has_required:
    df["Tarix"] = pd.to_datetime(df["Tarix"])
    df["Ümumi Gəlir ($)"] = df["Qiymət ($)"] * df["Günlük Satış"]
    
    if "Maya Dəyəri ($)" in df.columns:
        df["Ümumi Xərc ($)"] = df["Maya Dəyəri ($)"] * df["Günlük Satış"]
        df["Xalis Mənfəət ($)"] = df["Ümumi Gəlir ($)"] - df["Ümumi Xərc ($)"]

    st.sidebar.subheader("🔍 Filtr")
    product_list = list(df["Məhsul"].unique())
    selected_product = st.sidebar.selectbox("Məhsul Seçin:", product_list)

    filtered_df = df[df["Məhsul"] == selected_product].sort_values("Tarix")

    avg_price = filtered_df["Qiymət ($)"].mean()
    total_sales = filtered_df["Günlük Satış"].sum()
    total_revenue = filtered_df["Ümumi Gəlir ($)"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Aylıq Orta Qiymət", f"${avg_price:.2f}")
    col2.metric("Ümumi Satış (Ədəd)", f"{total_sales:,}")
    col3.metric("Ümumi Gəlir", f"${total_revenue:,.2f}")

    if "Xalis Mənfəət ($)" in filtered_df.columns:
        total_profit = filtered_df["Xalis Mənfəət ($)"].sum()
        col4.metric("Ümumi Mənfəət", f"${total_profit:,.2f}")

    st.markdown("---")

    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📈 Qiymət Dəyişmə Dinamikası")
        fig_price = px.line(
            filtered_df, 
            x="Tarix", 
            y="Qiymət ($)", 
            title=f"{selected_product} - Qiymət Tarixçəsi",
            markers=True
        )
        st.plotly_chart(fig_price, use_container_width=True)

    with g2:
        st.subheader("📊 Günlük Satış Həcmi")
        fig_sales = px.bar(
            filtered_df, 
            x="Tarix", 
            y="Günlük Satış", 
            title=f"{selected_product} - Günlük Satış Trendi"
        )
        st.plotly_chart(fig_sales, use_container_width=True)

    with st.expander("📋 Yüklənmiş Datanın Cədvəl Forması"):
        st.dataframe(filtered_df, use_container_width=True)

else:
    st.warning("⚠️ Yüklədiyiniz faylda bu vacib sütunlar tapılmadı:")
    st.write(f"Lazımi sütunlar: `Tarix`, `Məhsul`, `Qiymət ($)`, `Günlük Satış`")
    st.write("Faylınızdakı mövcud sütunlar bunlardır:")
    st.write(list(df.columns))
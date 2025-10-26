import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances

st.title("تشخیص داده‌های نویز با DBSCAN و وزن ناهنجاری")

uploaded_file = st.file_uploader("فایل Excel خود را بارگذاری کنید", type=["xlsx"])

if uploaded_file:
    df1 = pd.read_excel(uploaded_file)

    # انتخاب ستون‌های عددی برای تحلیل
    selected_columns = st.multiselect("ستون‌های عددی برای تحلیل را انتخاب کنید", df1.select_dtypes(include=np.number).columns.tolist)

    if selected_columns:
        # استانداردسازی داده‌ها
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df1[selected_columns])
        scaled_df = pd.DataFrame(scaled_data, columns=selected_columns)
        scaled_df_clean = scaled_df.dropna()

        # اجرای DBSCAN
        dbscan = DBSCAN(eps=0.7, min_samples=6)
        labels = dbscan.fit_predict(scaled_df_clean)

        df = scaled_df_clean.copy()
        df['dbscan_label'] = labels

        # جدا کردن داده‌های نویز و خوشه‌ها
        noise_mask = df['dbscan_label'] == -1
        cluster_mask = df['dbscan_label'] != -1

        noise_points = df[noise_mask].drop(columns='dbscan_label').values
        cluster_points = df[cluster_mask].drop(columns='dbscan_label').values

        # محاسبه فاصله نویزها از نزدیک‌ترین نقطه خوشه‌ای
        distances = pairwise_distances(noise_points, cluster_points)
        min_distances = distances.min(axis=1)

        # نرمال‌سازی فاصله‌ها
        normalized_weights = (min_distances - min_distances.min()) / (min_distances.max() - min_distances.min())

        # ساخت وزن ناهنجاری برای همه داده‌ها
        anomaly_weights = np.zeros(len(df))
        anomaly_weights[noise_mask.values] = normalized_weights
        df['anomaly_weight'] = anomaly_weights

        # تعریف نویز جدید بر اساس وزن > 0.5
        df['custom_noise'] = df['anomaly_weight'] > 0.5

        st.subheader("نتایج تشخیص ناهنجاری")
        st.write(df)

        st.subheader("دانلود خروجی")
        output = df.copy()
        output['original_index'] = output.index
        output = output[['original_index', 'anomaly_weight', 'custom_noise']]
        st.download_button("دانلود فایل خروجی", output.to_csv(index=False).encode('utf-8'), "anomaly_output.csv", "text/csv")

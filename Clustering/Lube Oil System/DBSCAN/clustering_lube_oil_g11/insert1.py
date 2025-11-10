import os
import pyodbc
import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
import joblib
import pymysql   # جایگزین mysql.connector
from datetime import datetime

# -----------------------------
# اتصال به SQL Server و دریافت آخرین مقادیر
# -----------------------------
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=MKZ-DSAS\\DSAS;'
    'DATABASE=DSAS;'
    'UID=datadriven;'
    'PWD=5Rdx@4Rfv1355'
)
cursor = conn.cursor()

asset_ids = [8341, 8342, 8343, 8344, 8346, 9286, 9287]
values = []

for asset_id in asset_ids:
    query = f"""
        SELECT TOP 1 [Value]
        FROM [PDA].[Periodic_Values]
        WHERE UnitID = 11 AND AssetID = {asset_id}
        ORDER BY DateTime DESC
    """
    cursor.execute(query)
    row = cursor.fetchone()
    values.append(row.Value if row else None)

cursor.close()
conn.close()

value_8341, value_8342, value_8343, value_8344, value_8346, value_9286, value_9287 = values

print("✅ مقادیر آخرین رکوردها برای UnitID=11:")
for aid, val in zip(asset_ids, values):
    print(f"AssetID {aid} → Value: {val}")

# -----------------------------
# بارگذاری اجزای مدل از همان پوشه اسکریپت
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

scaler = joblib.load(os.path.join(BASE_DIR, 'scaler.pkl'))
dbscan = joblib.load(os.path.join(BASE_DIR, 'dbscan_model.pkl'))
cluster_points = np.load(os.path.join(BASE_DIR, 'cluster_points.npy'))

# -----------------------------
# تابع تشخیص ناهنجاری
# -----------------------------
def is_anomalous(input_dict, threshold=10.0):
    input_df = pd.DataFrame([input_dict])
    scaled_input = scaler.transform(input_df)
    label = dbscan.fit_predict(scaled_input)[0]

    if label != -1:
        return {'is_anomaly': False, 'anomaly_weight': 0.0}

    distance = pairwise_distances(scaled_input, cluster_points).min()
    anomaly_weight = float(distance)
    is_anomaly = anomaly_weight > threshold
    return {'is_anomaly': is_anomaly, 'anomaly_weight': anomaly_weight}

sample_input = {
    'AssetID_8341': value_8341,
    'AssetID_8342': value_8342,
    'AssetID_8343': value_8343,
    'AssetID_8344': value_8344,
    'AssetID_8346': value_8346,
    'AssetID_9286': value_9286,
    'AssetID_9287': value_9287
}

result = is_anomalous(sample_input)
print("🔎 نتیجه تشخیص:", result)

# -----------------------------
# اتصال به MySQL با PyMySQL
# -----------------------------
conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",   # اگر پسورد دارید اینجا وارد کنید
    database="dsas",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.Cursor
)

cursor = conn.cursor()

inputs = values
anomaly_weight = result['anomaly_weight']
results = "Normal" if anomaly_weight < 5 else "Abnormal"
model_name = "Anomaly detection for lube oil system"
unitID = 21
system = "dbscan clustering weighted by computing distance from clusters"
score = anomaly_weight
created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
updated_at = created_at

query = """
    INSERT INTO results_dsas_mhi_lube_oil_11 
    (inputs, results, model_name, unitID, system, score, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

cursor.execute(query, (
    str(inputs),
    results,
    model_name,
    unitID,
    system,
    score,
    created_at,
    updated_at
))

conn.commit()
print("✅ داده با موفقیت ثبت شد.")

cursor.close()
conn.close()

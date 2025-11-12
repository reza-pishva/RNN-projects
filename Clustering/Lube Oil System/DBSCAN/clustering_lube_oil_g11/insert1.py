# import os
# import pyodbc
# import numpy as np
# import pandas as pd
# from sklearn.metrics import pairwise_distances
# import joblib
# import pymysql
# from datetime import datetime

# # -----------------------------
# # تعریف متغیر واحد برای UnitID
# # -----------------------------
# unitID = 11   # مقدار UnitID را اینجا تغییر بده

# # -----------------------------
# # اتصال به SQL Server و دریافت آخرین مقادیر
# # -----------------------------
# conn = pyodbc.connect(
#     'DRIVER={SQL Server};'
#     'SERVER=MKZ-DSAS\\DSAS;'
#     'DATABASE=DSAS;'
#     'UID=datadriven;'
#     'PWD=5Rdx@4Rfv1355'
# )

# cursor = conn.cursor()

# asset_ids = [8341, 8342, 8343, 8344, 8346, 9286, 9287]
# values = []
# record_date, record_time, record_datetime = None, None, None

# for asset_id in asset_ids:
#     if asset_id == 8341:
#         query = f"""
#             SELECT TOP 1 [Value], [RecordDate], [RecordTime], [DateTime]
#             FROM [PDA].[Periodic_Values]
#             WHERE UnitID = {unitID} AND AssetID = {asset_id}
#             ORDER BY DateTime DESC
#         """
#         cursor.execute(query)
#         row = cursor.fetchone()
#         if row:
#             values.append(row.Value)
#             record_date = row.RecordDate
#             record_time = row.RecordTime
#             record_datetime = row.DateTime
#         else:
#             values.append(None)
#     else:
#         query = f"""
#             SELECT TOP 1 [Value]
#             FROM [PDA].[Periodic_Values]
#             WHERE UnitID = {unitID} AND AssetID = {asset_id}
#             ORDER BY DateTime DESC
#         """
#         cursor.execute(query)
#         row = cursor.fetchone()
#         values.append(row.Value if row else None)

# cursor.close()
# conn.close()

# value_8341, value_8342, value_8343, value_8344, value_8346, value_9286, value_9287 = values

# print(f"✅ مقادیر آخرین رکوردها برای UnitID={unitID}:")
# for aid, val in zip(asset_ids, values):
#     print(f"AssetID {aid} → Value: {val}")

# print(f"📌 RecordDate: {record_date}, RecordTime: {record_time}, DateTime: {record_datetime}")

# # -----------------------------
# # بارگذاری اجزای مدل
# # -----------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# scaler = joblib.load(os.path.join(BASE_DIR, 'scaler.pkl'))
# dbscan = joblib.load(os.path.join(BASE_DIR, 'dbscan_model.pkl'))
# cluster_points = np.load(os.path.join(BASE_DIR, 'cluster_points.npy'))

# # -----------------------------
# # تابع تشخیص ناهنجاری
# # -----------------------------
# def is_anomalous(input_dict, threshold=10.0):
#     input_df = pd.DataFrame([input_dict])
#     scaled_input = scaler.transform(input_df)
#     label = dbscan.fit_predict(scaled_input)[0]

#     if label != -1:
#         return {'is_anomaly': False, 'anomaly_weight': 0.0}

#     distance = pairwise_distances(scaled_input, cluster_points).min()
#     anomaly_weight = float(distance)
#     is_anomaly = anomaly_weight > threshold
#     return {'is_anomaly': is_anomaly, 'anomaly_weight': anomaly_weight}

# sample_input = {
#     'AssetID_8341': value_8341,
#     'AssetID_8342': value_8342,
#     'AssetID_8343': value_8343,
#     'AssetID_8344': value_8344,
#     'AssetID_8346': value_8346,
#     'AssetID_9286': value_9286,
#     'AssetID_9287': value_9287
# }

# result = is_anomalous(sample_input)
# print("🔎 نتیجه تشخیص:", result)

# # -----------------------------
# # اتصال به MySQL با PyMySQL
# # -----------------------------
# conn = pymysql.connect(
#     host="127.0.0.1",
#     port=3306,
#     user="root",
#     password="",
#     database="dsas",
#     charset="utf8mb4",
#     cursorclass=pymysql.cursors.Cursor
# )

# cursor = conn.cursor()

# inputs = values
# anomaly_weight = result['anomaly_weight']
# results = "Normal" if anomaly_weight < 5 else "Abnormal"
# model_name = "Anomaly detection for lube oil system"
# system = "dbscan clustering weighted by computing distance from clusters"
# score = anomaly_weight
# created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# updated_at = created_at

# query = """
#     INSERT INTO results_dsas_mhi_lube_oil_11 
#     (inputs, results, model_name, unitID, system, score, RecordDate, RecordTime, DateTime, created_at, updated_at)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
# """

# cursor.execute(query, (
#     str(inputs),
#     results,
#     model_name,
#     unitID,
#     system,
#     score,
#     record_date,
#     record_time,
#     record_datetime,
#     created_at,
#     updated_at
# ))

# conn.commit()
# print("✅ داده با موفقیت ثبت شد.")

# cursor.close()
# conn.close()
# import os
# import pyodbc
# import numpy as np
# import pandas as pd
# from sklearn.metrics import pairwise_distances
# import joblib
# import pymysql
# from datetime import datetime
# import time   # برای sleep

# # -----------------------------
# # تعریف متغیر واحد برای UnitID
# # -----------------------------
# unitID = 11   # مقدار UnitID را اینجا تغییر بده

# # -----------------------------
# # بارگذاری اجزای مدل (یکبار کافی است)
# # -----------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# scaler = joblib.load(os.path.join(BASE_DIR, 'scaler.pkl'))
# dbscan = joblib.load(os.path.join(BASE_DIR, 'dbscan_model.pkl'))
# cluster_points = np.load(os.path.join(BASE_DIR, 'cluster_points.npy'))

# # -----------------------------
# # تابع تشخیص ناهنجاری
# # -----------------------------
# def is_anomalous(input_dict, threshold=10.0):
#     input_df = pd.DataFrame([input_dict])
#     scaled_input = scaler.transform(input_df)
#     label = dbscan.fit_predict(scaled_input)[0]

#     if label != -1:
#         return {'is_anomaly': False, 'anomaly_weight': 0.0}

#     distance = pairwise_distances(scaled_input, cluster_points).min()
#     anomaly_weight = float(distance)
#     is_anomaly = anomaly_weight > threshold
#     return {'is_anomaly': is_anomaly, 'anomaly_weight': anomaly_weight}

# # -----------------------------
# # حلقه اجرا هر 5 دقیقه
# # -----------------------------
# while True:
#     try:
#         # اتصال به SQL Server و دریافت آخرین مقادیر
#         conn = pyodbc.connect(
#             'DRIVER={SQL Server};'
#             'SERVER=MKZ-DSAS\\DSAS;'
#             'DATABASE=DSAS;'
#             'UID=datadriven;'
#             'PWD=5Rdx@4Rfv1355'
#         )
#         cursor = conn.cursor()

#         asset_ids = [8341, 8342, 8343, 8344, 8346, 9286, 9287]
#         values = []
#         record_date, record_time, record_datetime = None, None, None

#         for asset_id in asset_ids:
#             if asset_id == 8341:
#                 query = f"""
#                     SELECT TOP 1 [Value], [RecordDate], [RecordTime], [DateTime]
#                     FROM [PDA].[Periodic_Values]
#                     WHERE UnitID = {unitID} AND AssetID = {asset_id}
#                     ORDER BY DateTime DESC
#                 """
#                 cursor.execute(query)
#                 row = cursor.fetchone()
#                 if row:
#                     values.append(row.Value)
#                     record_date = row.RecordDate
#                     record_time = row.RecordTime
#                     record_datetime = row.DateTime
#                 else:
#                     values.append(None)
#             else:
#                 query = f"""
#                     SELECT TOP 1 [Value]
#                     FROM [PDA].[Periodic_Values]
#                     WHERE UnitID = {unitID} AND AssetID = {asset_id}
#                     ORDER BY DateTime DESC
#                 """
#                 cursor.execute(query)
#                 row = cursor.fetchone()
#                 values.append(row.Value if row else None)

#         cursor.close()
#         conn.close()

#         # آماده‌سازی ورودی برای مدل
#         sample_input = {
#             'AssetID_8341': values[0],
#             'AssetID_8342': values[1],
#             'AssetID_8343': values[2],
#             'AssetID_8344': values[3],
#             'AssetID_8346': values[4],
#             'AssetID_9286': values[5],
#             'AssetID_9287': values[6]
#         }

#         result = is_anomalous(sample_input)
#         print("🔎 نتیجه تشخیص:", result)

#         # اتصال به MySQL و ذخیره داده
#         conn = pymysql.connect(
#             host="127.0.0.1",
#             port=3306,
#             user="root",
#             password="",
#             database="dsas",
#             charset="utf8mb4",
#             cursorclass=pymysql.cursors.Cursor
#         )
#         cursor = conn.cursor()

#         inputs = values
#         anomaly_weight = result['anomaly_weight']
#         results = "Normal" if anomaly_weight < 5 else "Abnormal"
#         model_name = "Anomaly detection for lube oil system"
#         system = "dbscan clustering weighted by computing distance from clusters"
#         score = anomaly_weight
#         created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         updated_at = created_at

#         query = """
#             INSERT INTO results_dsas_mhi_lube_oil_11 
#             (inputs, results, model_name, unitID, system, score, RecordDate, RecordTime, DateTime, created_at, updated_at)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """

#         cursor.execute(query, (
#             str(inputs),
#             results,
#             model_name,
#             unitID,
#             system,
#             score,
#             record_date,
#             record_time,
#             record_datetime,
#             created_at,
#             updated_at
#         ))

#         conn.commit()
#         print("✅ داده با موفقیت ثبت شد.")

#         cursor.close()
#         conn.close()

#     except Exception as e:
#         print("❌ خطا رخ داد:", e)

#     # توقف 5 دقیقه‌ای
#     print("⏳ منتظر اجرای بعدی...")
#     time.sleep(120)  # 300 ثانیه = 5 دقیقه

# import os
# import pyodbc
# import numpy as np
# import pandas as pd
# from sklearn.metrics import pairwise_distances
# import joblib
# import pymysql
# from datetime import datetime
# import time   # برای sleep

# # -----------------------------
# # تعریف متغیر واحد برای UnitID
# # -----------------------------
# unitID = 11   # مقدار UnitID را اینجا تغییر بده

# # -----------------------------
# # بارگذاری اجزای مدل (یکبار کافی است)
# # -----------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# scaler = joblib.load(os.path.join(BASE_DIR, 'scaler.pkl'))
# dbscan = joblib.load(os.path.join(BASE_DIR, 'dbscan_model.pkl'))
# cluster_points = np.load(os.path.join(BASE_DIR, 'cluster_points.npy'))

# # -----------------------------
# # تابع تشخیص ناهنجاری
# # -----------------------------
# def is_anomalous(input_dict, threshold=10.0):
#     input_df = pd.DataFrame([input_dict])
#     scaled_input = scaler.transform(input_df)
#     label = dbscan.fit_predict(scaled_input)[0]

#     if label != -1:
#         return {'is_anomaly': False, 'anomaly_weight': 0.0}

#     distance = pairwise_distances(scaled_input, cluster_points).min()
#     anomaly_weight = float(distance)
#     is_anomaly = anomaly_weight > threshold
#     return {'is_anomaly': is_anomaly, 'anomaly_weight': anomaly_weight}

# # -----------------------------
# # حلقه اجرا هر 5 دقیقه
# # -----------------------------
# while True:
#     try:
#         # اتصال به SQL Server و دریافت آخرین مقادیر
#         conn = pyodbc.connect(
#             'DRIVER={SQL Server};'
#             'SERVER=MKZ-DSAS\\DSAS;'
#             'DATABASE=DSAS;'
#             'UID=datadriven;'
#             'PWD=5Rdx@4Rfv1355'
#         )
#         cursor = conn.cursor()

#         asset_ids = [8341, 8342, 8343, 8344, 8346, 9286, 9287]
#         values = []
#         record_date, record_time, record_datetime = None, None, None

#         for asset_id in asset_ids:
#             if asset_id == 8341:
#                 query = f"""
#                     SELECT TOP 1 [Value], [RecordDate], [RecordTime], [DateTime]
#                     FROM [PDA].[Periodic_Values]
#                     WHERE UnitID = {unitID} AND AssetID = {asset_id}
#                     ORDER BY DateTime DESC
#                 """
#                 cursor.execute(query)
#                 row = cursor.fetchone()
#                 if row:
#                     values.append(row.Value)
#                     record_date = row.RecordDate
#                     record_time = row.RecordTime
#                     record_datetime = row.DateTime
#                 else:
#                     values.append(None)
#             else:
#                 query = f"""
#                     SELECT TOP 1 [Value]
#                     FROM [PDA].[Periodic_Values]
#                     WHERE UnitID = {unitID} AND AssetID = {asset_id}
#                     ORDER BY DateTime DESC
#                 """
#                 cursor.execute(query)
#                 row = cursor.fetchone()
#                 values.append(row.Value if row else None)

#         cursor.close()
#         conn.close()

#         # آماده‌سازی ورودی برای مدل
#         sample_input = {
#             'AssetID_8341': values[0],
#             'AssetID_8342': values[1],
#             'AssetID_8343': values[2],
#             'AssetID_8344': values[3],
#             'AssetID_8346': values[4],
#             'AssetID_9286': values[5],
#             'AssetID_9287': values[6]
#         }

#         result = is_anomalous(sample_input)
#         print("🔎 نتیجه تشخیص:", result)

#         # اتصال به MySQL و ذخیره داده
#         conn = pymysql.connect(
#             host="127.0.0.1",
#             port=3306,
#             user="root",
#             password="",
#             database="dsas",
#             charset="utf8mb4",
#             cursorclass=pymysql.cursors.Cursor
#         )
#         cursor = conn.cursor()

#         anomaly_weight = result['anomaly_weight']
#         results = "Normal" if anomaly_weight < 5 else "Abnormal"
#         model_name = "dbscan clustering weighted by computing distance from clusters"
#         system = "Anomaly detection for lube oil system"
#         score = anomaly_weight
#         created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         updated_at = created_at

#         query = """
#             INSERT INTO results_dsas_mhi_lube_oil_11 
#             (AssetID_8341, AssetID_8342, AssetID_8343, AssetID_8344, AssetID_8346, AssetID_9286, AssetID_9287,
#              results, model_name, unitID, system, score, RecordDate, RecordTime, DateTime, created_at, updated_at)
#             VALUES (%s, %s, %s, %s, %s, %s, %s,
#                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """

#         cursor.execute(query, (
#             values[0],  # AssetID_8341
#             values[1],  # AssetID_8342
#             values[2],  # AssetID_8343
#             values[3],  # AssetID_8344
#             values[4],  # AssetID_8346
#             values[5],  # AssetID_9286
#             values[6],  # AssetID_9287
#             results,
#             model_name,
#             unitID,
#             system,
#             score,
#             record_date,
#             record_time,
#             record_datetime,
#             created_at,
#             updated_at
#         ))

#         conn.commit()
#         print("✅ داده با موفقیت ثبت شد.")

#         cursor.close()
#         conn.close()

#     except Exception as e:
#         print("❌ خطا رخ داد:", e)

#     # توقف 5 دقیقه‌ای
#     print("⏳ منتظر اجرای بعدی...")
#     time.sleep(60)  # 300 ثانیه = 5 دقیقه


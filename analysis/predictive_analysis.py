import boto3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor

# 1) Connect to DynamoDB Local
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://host.docker.internal:8000',
    region_name='us-east-2',
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy'
)
table = dynamodb.Table('BatteryData')

# 2) Fetch data from DynamoDB
response = table.scan()
data = response['Items']
df = pd.DataFrame(data)

# 3) Convert columns to proper data types
df['state_of_charge'] = pd.to_numeric(df['state_of_charge'])
df['temperature'] = pd.to_numeric(df['temperature'])
df['voltage'] = pd.to_numeric(df['voltage'])
df['timestamp'] = pd.to_datetime(df['timestamp'])

# If "state" exists, encode it as a categorical feature
if 'state' in df.columns:
    df['state'] = df['state'].astype('category').cat.codes
else:
    # If no 'state' column, create a dummy column
    df['state'] = 0

# 4) Sort and select a single battery for demonstration
df = df.sort_values(by=['battery_id', 'timestamp'])
battery_id = 'battery-25'
df_battery = df[df['battery_id'] == battery_id].copy()

if df_battery.empty:
    print(f"No data found for {battery_id}")
    exit()

# 5) Create numeric timestamp
df_battery['timestamp_numeric'] = df_battery['timestamp'].astype(np.int64) // 10**9

# 6) Define features (X) and target (y)
X = df_battery[['timestamp_numeric', 'temperature', 'voltage', 'state']]
y = df_battery['state_of_charge']

# 7) Train a Random Forest model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# 8) Predict on the same data (for demonstration)
df_battery['predicted_soc'] = model.predict(X)

# 9) Plot the results
plt.figure(figsize=(10, 6))
plt.plot(df_battery['timestamp'], df_battery['state_of_charge'], 'o-', label='Actual SOC')
plt.plot(df_battery['timestamp'], df_battery['predicted_soc'], 'x--', label='Predicted SOC')
plt.xlabel('Time')
plt.ylabel('State of Charge (%)')
plt.title(f'Random Forest SOC Prediction for {battery_id}')
plt.legend()
plt.tight_layout()
plt.show()

import requests
import json
import random
import time
from datetime import datetime, timezone

API_ENDPOINT = "http://127.0.0.1:3000/battery_data"

# Initialize counters and settings
battery_id_counter = 1
data_points_per_battery = 10
data_points_sent_for_current_battery = 0

def generate_random_battery_data():
    global battery_id_counter
    # Build the battery ID from the counter
    battery_id = f"battery-{battery_id_counter}"
    data = {
        "battery_id": battery_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state_of_charge": round(random.uniform(20.0, 100.0), 2),
        "temperature": round(random.uniform(20.0, 40.0), 2),
        "voltage": round(random.uniform(3.0, 4.2), 2)
    }
    return data

def send_data_to_api(data):
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(API_ENDPOINT, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            print("Data successfully sent:", data)
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print(f"Error sending data: {str(e)}")

def main():
    global battery_id_counter, data_points_sent_for_current_battery
    while True:
        data = generate_random_battery_data()
        send_data_to_api(data)
        data_points_sent_for_current_battery += 1

        # After sending a fixed number of data points for the current battery, move to the next one.
        if data_points_sent_for_current_battery >= data_points_per_battery:
            battery_id_counter += 1
            data_points_sent_for_current_battery = 0

        time.sleep(5)

if __name__ == "__main__":
    main()
#first i rab
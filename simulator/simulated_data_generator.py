import requests
import json
import random
import time
from datetime import datetime, timezone

API_ENDPOINT = "http://127.0.0.1:3000/battery_data"

# Configuration: each battery sends 10 readings
data_points_per_battery = 10

# Global counters and state storage
battery_id_counter = 1
data_points_sent_for_current_battery = 0
# Start with an initial state-of-charge for the current battery
current_state_of_charge = 100.0

def generate_battery_data():
    global current_state_of_charge, battery_id_counter
    battery_id = f"battery-{battery_id_counter}"
    
    # Simulate a gradual decay in state-of-charge for this battery
    # with a small random variation around a decreasing trend.
    decay = random.uniform(0.5, 1.5)  # each reading decreases SOC by ~0.5 to 1.5%
    current_state_of_charge = max(0, current_state_of_charge - decay)
    
    data = {
        "battery_id": battery_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state_of_charge": round(current_state_of_charge, 2),
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
    global battery_id_counter, data_points_sent_for_current_battery, current_state_of_charge
    while True:
        data = generate_battery_data()
        send_data_to_api(data)
        data_points_sent_for_current_battery += 1

        # When we've sent the designated number of readings for the current battery,
        # reset the counter and "replace" the battery (i.e. increment battery ID)
        # and reset the state-of-charge to 100%.
        if data_points_sent_for_current_battery >= data_points_per_battery:
            battery_id_counter += 1
            data_points_sent_for_current_battery = 0
            current_state_of_charge = 100.0

        time.sleep(5)

if __name__ == "__main__":
    main()

import requests
import json
import random
import time
from datetime import datetime, timezone

API_ENDPOINT = "http://127.0.0.1:3000/battery_data"

# Simulation parameters
TIME_STEP_SECONDS = 5
NUMBER_OF_READINGS_PER_BATTERY = 50
NUMBER_OF_BATTERIES = 30  # You can adjust this as needed

# Probability of each state
PROB_DRIVING = 0.5    # 50% chance we are driving (discharging)
PROB_CHARGING = 0.2   # 20% chance we are charging
PROB_IDLE = 0.3       # 30% chance we are idle

# Rates of SOC change per time step (5s)
DISCHARGE_RATE = (0.2, 0.8)      # lose 0.2% to 0.8% per 5s while driving
CHARGE_RATE = (0.3, 1.0)         # gain 0.3% to 1.0% per 5s while charging
SELF_DISCHARGE_RATE = (0.0, 0.05) # lose up to 0.05% every 5s while idle

# Temperature behavior
AMBIENT_TEMP = 25.0  # baseline ambient temperature
DRIVE_TEMP_RISE = (0.1, 0.3)   # rise per 5s while driving
CHARGE_TEMP_RISE = (0.05, 0.2) # rise per 5s while charging
IDLE_TEMP_COOL = (0.0, 0.1)    # cool down (or slightly warm) toward ambient

def send_data_to_api(data):
    """
    Sends the generated data to the API endpoint via a POST request.
    """
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

def simulate_battery(battery_id):
    """
    Simulates a single battery's readings over multiple cycles,
    modeling driving, charging, and idle states.
    """
    # Initialize battery parameters
    soc = 100.0   # start fully charged
    temperature = AMBIENT_TEMP
    voltage = 4.2 # near full charge for Li-ion cell

    for _ in range(NUMBER_OF_READINGS_PER_BATTERY):
        # Decide the battery's state based on random probabilities
        r = random.random()
        if r < PROB_DRIVING:
            state = "driving"
        elif r < PROB_DRIVING + PROB_CHARGING:
            state = "charging"
        else:
            state = "idle"

        # Update SOC, temperature, and voltage based on the chosen state
        if state == "driving":
            delta_soc = random.uniform(*DISCHARGE_RATE)
            soc = max(0, soc - delta_soc)
            temp_rise = random.uniform(*DRIVE_TEMP_RISE)
            temperature += temp_rise
            voltage = 3.0 + (soc / 100) * 1.2  # simplistic approximation

        elif state == "charging":
            delta_soc = random.uniform(*CHARGE_RATE)
            soc = min(100, soc + delta_soc)
            temp_rise = random.uniform(*CHARGE_TEMP_RISE)
            temperature += temp_rise
            voltage = 3.0 + (soc / 100) * 1.2

        else:  # idle
            delta_soc = random.uniform(*SELF_DISCHARGE_RATE)
            soc = max(0, soc - delta_soc)
            # Adjust temperature toward ambient
            if temperature > AMBIENT_TEMP:
                temperature -= random.uniform(*IDLE_TEMP_COOL)
            else:
                temperature += random.uniform(0, 0.05)
            voltage = 3.0 + (soc / 100) * 1.2

        # Build the data payload including the state field
        data_payload = {
            "battery_id": f"battery-{battery_id}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state_of_charge": round(soc, 2),
            "temperature": round(temperature, 2),
            "voltage": round(voltage, 2),
            "state": state  # New field indicating the current state
        }

        # Send data to your Lambda/API
        send_data_to_api(data_payload)
        time.sleep(TIME_STEP_SECONDS)

def main():
    """
    Main entry point to simulate the specified number of batteries.
    """
    for battery_id in range(1, NUMBER_OF_BATTERIES + 1):
        simulate_battery(battery_id)

if __name__ == "__main__":
    main()

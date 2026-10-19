import pandas as pd
from datetime import datetime, timedelta
import random

def generate_mock_flights(num_days=30):
    """
    Generates a realistic schedule of flights out of Harare (HRE)
    spanning `num_days` from today.
    """
    routes_database = [
        # Regional High-Volume Routes (Cross-border / Business)
        {"airline": "Fastjet", "flight_number": "FN8331", "destination": "Johannesburg (JNB)", "code": "JNB", "type": "Regional", "base_price": 220, "time": "07:25"},
        {"airline": "Fastjet", "flight_number": "FN8335", "destination": "Johannesburg (JNB)", "code": "JNB", "type": "Regional", "base_price": 210, "time": "17:10"},
        {"airline": "Airlink", "flight_number": "4Z109", "destination": "Johannesburg (JNB)", "code": "JNB", "type": "Regional", "base_price": 245, "time": "07:10"},
        {"airline": "Airlink", "flight_number": "4Z383", "destination": "Cape Town (CPT)", "code": "CPT", "type": "Regional", "base_price": 360, "time": "09:25"},
        {"airline": "Airlink", "flight_number": "4Z411", "destination": "Durban (DUR)", "code": "DUR", "type": "Regional", "base_price": 310, "time": "13:25"},
        
        # Domestic Tourism & Business Routes
        {"airline": "Fastjet", "flight_number": "FN8003", "destination": "Victoria Falls (VFA)", "code": "VFA", "type": "Domestic", "base_price": 140, "time": "08:50"},
        {"airline": "Fastjet", "flight_number": "FN8441", "destination": "Bulawayo (BUQ)", "code": "BUQ", "type": "Domestic", "base_price": 110, "time": "06:00"},
        {"airline": "Air Zimbabwe", "flight_number": "UM322", "destination": "Victoria Falls (VFA)", "code": "VFA", "type": "Domestic", "base_price": 125, "time": "07:30"},
        
        # East / Central Africa Regional Routes (Trade & Connections)
        {"airline": "Ethiopian Airlines", "flight_number": "ET034", "destination": "Lilongwe (LLW)", "code": "LLW", "type": "Regional", "base_price": 290, "time": "13:50"},
        {"airline": "Ethiopian Airlines", "flight_number": "ET892", "destination": "Addis Ababa (ADD)", "code": "ADD", "type": "International", "base_price": 680, "time": "02:20"},
        {"airline": "Kenya Airways", "flight_number": "KQ706", "destination": "Nairobi (NBO)", "code": "NBO", "type": "Regional", "base_price": 520, "time": "11:55"},
        {"airline": "RwandAir", "flight_number": "WB112", "destination": "Kigali (KGL)", "code": "KGL", "type": "Regional", "base_price": 450, "time": "17:00"},
        {"airline": "Air Zimbabwe", "flight_number": "UM438", "destination": "Dar es Salaam (DAR)", "code": "DAR", "type": "Regional", "base_price": 380, "time": "11:00"}
    ]

    flight_records = []
    start_date = datetime.now()

    flight_id_counter = 1000

    for day in range(num_days):
        current_date = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
        
        for route in routes_database:
            flight_id_counter += 1
            # Add small random price fluctuations to simulate dynamic pricing
            price_variance = random.choice([-15, -10, 0, 10, 20, 35])
            final_price = max(80, route["base_price"] + price_variance)
            
            flight_records.append({
                "flight_id": f"FL-{flight_id_counter}",
                "airline": route["airline"],
                "flight_number": route["flight_number"],
                "origin": "Harare (HRE)",
                "destination": route["destination"],
                "dest_code": route["code"],
                "flight_date": current_date,
                "departure_time": route["time"],
                "flight_type": route["type"],
                "price_usd": final_price
            })

    return pd.DataFrame(flight_records)

if __name__ == "__main__":
    df = generate_mock_flights(num_days=14)
    df.to_csv("data/flights.csv", index=False)
    print(f"Generated {len(df)} flight records into data/flights.csv")
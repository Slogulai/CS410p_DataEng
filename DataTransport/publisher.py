from google.cloud import pubsub_v1
from google.oauth2 import service_account
import requests
import json
from datetime import datetime

# Explicitly load credentials from the key file.
credentials = service_account.Credentials.from_service_account_file(
    "/Users/christophersloggett/CS410_DataEng/DataTransport/key.json"
)
publisher = pubsub_v1.PublisherClient(credentials=credentials)
topic_path = "projects/bubsub69/subscriptions/bus_data-sub"  

message_counter = 0

bus_ids = [ 2901,2914,2922,2938,3009,3010,3016,3018,3019,3021,3023,3031,3032,3033,3034,3038,3042,3045,3102,3104,
            3108,3112,3113,3117,3123,3124,3125,3127,3130,3134,3139,3140,3143,3145,3153,3157,3160,3163,3202,3203,
            3206,3209,3210,3220,3224,3225,3229,3233,3234,3240,3241,3242,3243,3245,3246,3248,3249,3251,3257,3261,
            3262,3264,3268,3305,3314,3321,3404,3409,3410,3415,3416,3419,3501,3502,3504,3505,3506,3507,3509,3511,
            3513,3514,3516,3519,3523,3524,3533,3535,3537,3542,3543,3544,3545,3546,3547,3553,3559,3566,3567,3569 ]

# Function to fetch data from the API
def fetch_bus_data(bus_id):
    api_url = f"https://busdata.cs.pdx.edu/api/getBreadCrumbs?vehicle_id={bus_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  
        return response.json()  
    except requests.RequestException as e:
        print(f"Error fetching data for bus {bus_id}: {e}")
        return None

# Function to publish messages to Pub/Sub
def publish_message(data):
    global message_counter
    try:
        message_data = json.dumps(data).encode("utf-8")
        future = publisher.publish(topic_path, message_data)

        message_counter += 1

        if message_counter % 50000 == 0:
            print(f"Published {message_counter} messages so far...")
    except Exception as e:
        print(f"Error publishing message: {e}")

if __name__ == "__main__":
    for bus_id in bus_ids:
        bus_data = fetch_bus_data(bus_id)
        if bus_data:  
            if isinstance(bus_data, list):
                for data in bus_data:
                    data["timestamp"] = datetime.now().isoformat()  
                    publish_message(data)
            elif isinstance(bus_data, dict):
                bus_data["timestamp"] = datetime.now().isoformat()  
                publish_message(bus_data)
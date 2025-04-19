from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from datetime import datetime
import os
import json
import atexit

project_id = "bubsub69"
subscription_id = "Subbub"  
timeout = 1000.0

credentials = service_account.Credentials.from_service_account_file(
    "/Users/christophersloggett/CS410_DataEng/DataTransport/key.json"
)
subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
subscription_path = subscriber.subscription_path(project_id, subscription_id)

output_file = f"bus_data_{datetime.today().strftime('%Y%m%d_%H%M%S')}.json"

with open(output_file, 'w') as f:
    f.write('')

message_counter = 0

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    global message_counter
    try:
        data = json.loads(message.data.decode('utf-8'))

        with open(output_file, 'a') as f:
            if os.path.getsize(output_file) == 0:
                f.write('[\n')  
            else:
                f.write(',\n')  
            f.write(json.dumps(data))

        message_counter += 1

        if message_counter % 50000 == 0:
            print(f"Processed {message_counter} messages so far...")

        message.ack()  
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()  

def finalize_json_file():
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, 'a') as f:
            f.write('\n]')  

atexit.register(finalize_json_file)

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}...\n")

with subscriber:
    try:
        streaming_pull_future.result(timeout=timeout)
    except TimeoutError:
        print("No more messages within the timeout period.")
        streaming_pull_future.cancel()  
        streaming_pull_future.result()  

print(f"Messages written to {output_file}.")
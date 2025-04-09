from google.cloud import pubsub_v1
import os
import json

# TODO(developer)
project_id = "bubsub69"
topic_id = "bubsub"

publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)
count = 0
# Use the script's directory to locate the JSON file
json_files = [os.path.join(os.path.dirname(__file__), "bcsample.json")]
for file in json_files:
    with open(file, "r", encoding="utf-8") as f:
        records = json.load(f)
        for record in records:
            data = json.dumps(record).encode("utf-8")
            future = publisher.publish(topic_path, data)
            count += 1
            #print(f"Published record from {file} with message id: {future.result()}")

print(f"Published messages to {topic_path}. Total messages: {count}")
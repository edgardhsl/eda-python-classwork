from kafka import KafkaClient, TopicPartition, consumer
from time import sleep
import json

from kafka.consumer.group import KafkaConsumer

validator_panel = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

partition = TopicPartition("validator", 0)
validator_panel.assign([partition])

validator_panel.seek_to_beginning(partition)
offset = 0
while True:
    print("Waiting for reviewer to allow didactic materials.")

    for revision in validator_panel:
        offset = revision.offset + 1

        revision_data = json.loads(revision.value)
        print("review data: ", revision_data)

    validator_panel.seek(partition, offset)

    sleep(5)

# review_panel.close()
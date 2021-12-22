from kafka import KafkaClient, TopicPartition, consumer
from time import sleep
import json

from kafka.consumer.group import KafkaConsumer

review_panel = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

partition = TopicPartition("material_revision", 0)
review_panel.assign([partition])

review_panel.seek_to_beginning(partition)
offset = 0
while True:
    print("Waiting for materials to review...")

    for revision in review_panel:
        offset = revision.offset + 1

        revision_data = json.loads(revision.value)
        print("review data: ", revision_data)

    review_panel.seek(partition, offset)

    sleep(5)

# review_panel.close()
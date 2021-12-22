from kafka import KafkaClient, TopicPartition, consumer
from time import sleep
import json

from kafka.consumer.group import KafkaConsumer

material_panel = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

particao = TopicPartition("didadic_material", 0)
material_panel.assign([particao])

material_panel.seek_to_beginning(particao)
offset = 0
while True:
    print("Waiting for new materials...")
        
    for material in material_panel:
        offset = material.offset + 1

        material_data = json.loads(material.value)
        print("material info: ", material_data)

    material_panel.seek(particao, offset)

    sleep(5)

# painel_de_vendas.close()
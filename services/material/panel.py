from kafka import KafkaClient, TopicPartition, consumer
from time import sleep
import json

from kafka.consumer.group import KafkaConsumer

painel_de_vendas = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

particao = TopicPartition("didadic_material", 0)
painel_de_vendas.assign([particao])

painel_de_vendas.seek_to_beginning(particao)
offset = 0
while True:
    print("Waiting for new materials...")
        
    for pedido in painel_de_vendas:
        offset = pedido.offset + 1

        dados_do_pedido = json.loads(pedido.value)
        print("material info: ", dados_do_pedido)

    painel_de_vendas.seek(particao, offset)

    sleep(5)

# painel_de_vendas.close()
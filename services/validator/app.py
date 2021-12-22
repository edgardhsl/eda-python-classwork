from flask_apscheduler import APScheduler

from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import random
import json

PROCESS = "validator"
PROCESS_REVISION = "material_revision"

def start():
    global offset
    offset = 0

    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"], api_version=(0, 10, 1))
    cliente.add_topic(PROCESS)
    cliente.close()

def validate_material(material_to_review):
    valid, message = (material_to_review["success"] == 1), ""
    if valid:
        valid = (random.randint(1, 2) > int(material_to_review["min_approvals"]))
        if valid:
            message = "Material " + material_to_review["material"] + " autorizado pelo revisor " + material_to_review["reviewer"]
        else:
            message = "Material não liberado"
    else:
        message = "Não há revisor para liberar o material"
    
    return valid, message

def execute():
    global offset
    result = "ok"
    
    # recupera resultados do processo anterior
    revision_consumer = KafkaConsumer(
        bootstrap_servers=["kafka:29092"],
        auto_offset_reset='earliest',
        consumer_timeout_ms=1000,
        api_version=(0, 10, 1))
    partition = TopicPartition(PROCESS_REVISION, 0)
    revision_consumer.assign([partition])
    revision_consumer.seek(partition, offset)

    for revision in revision_consumer:
        offset = revision.offset + 1

        revision_info = json.loads(revision.value)

        valid, message = validate_material(revision_info)
        if valid:
            # simula algum processamento atraves de espera ocupada
            sleep(4)

            revision_info["success"] = 1
        else:
            revision_info["success"] = 0
            
        revision_info["message"] = message

        try:
            produtor = KafkaProducer(bootstrap_servers=["kafka:29092"], api_version=(0, 10, 1))
            produtor.send(topic=PROCESS, value=json.dumps(revision_info).encode("utf-8"))
        except KafkaError as erro:
            result = f"erro: {erro}"

    # o certo eh imprimir em (ou enviar para) um log de resultados
    print(result)


if __name__ == "__main__":
    start()

    scheduler = APScheduler()
    scheduler.add_job(id=PROCESS, func=execute,
                      trigger="interval", seconds=3)
    scheduler.start()

    while True:
        sleep(60)
from flask_apscheduler import APScheduler

from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import json

PROCESS = "material_revision"
PROCESS_DIDATIC_MATERIAL = "didadic_material"

def start():
    global offset
    offset = 0

    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"], api_version=(0, 10, 1))
    cliente.add_topic(PROCESS)
    cliente.close()


REVIEWERS_DATA = "/workdir/reviewers.json"
def validate_validator(material_to_review):
    valid, message = (material_to_review["success"] == 1), ""

    if valid:
        with open(REVIEWERS_DATA, "r") as file:
            reviewers = json.load(file)
            reviewer = next((x for x in reviewers if x["id"] == material_to_review["id_revisor"]), None)
            print(reviewer)
            valid = True if reviewer else False
                
            if valid:
                message = "O revisor foi" + reviewer["reviewer"] + " foi notificado por e-mail e irá avaliar o material."
            else:
                message = "O revisor informado não existe."
                
            file.close()
    else:
        message = "O processo de envio para revisão não foi concluído com sucesso."

    return valid, reviewer["reviewer"], material_to_review["title"], material_to_review["min_approvals"], message

def execute():
    global offset
    result = "ok"
    
    # recupera resultados do processo anterior
    revision_consumer = KafkaConsumer(
        bootstrap_servers=["kafka:29092"],
        auto_offset_reset='earliest',
        consumer_timeout_ms=1000,
        api_version=(0, 10, 1))
    partition = TopicPartition(PROCESS_DIDATIC_MATERIAL, 0)
    revision_consumer.assign([partition])
    revision_consumer.seek(partition, offset)

    for revision in revision_consumer:
        offset = revision.offset + 1

        material_info = json.loads(revision.value)

        valida, reviewer, material, min_approvals, message = validate_validator(material_info)
        if valida:
            # simula algum processamento atraves de espera ocupada
            sleep(4)

            material_info["success"] = 1
        else:
            material_info["success"] = 0

        material_info["reviewer"] = reviewer
        material_info["material"] = material
        material_info["min_approvals"] = min_approvals
        material_info["message"] = message

        try:
            produtor = KafkaProducer(
                bootstrap_servers=["kafka:29092"], api_version=(0, 10, 1))
            produtor.send(topic=PROCESS, value=json.dumps(material_info).encode("utf-8"))
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
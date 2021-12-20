from sys import api_version
from flask import Flask, jsonify

from kafka import KafkaClient, KafkaProducer
from kafka.errors import KafkaError

from time import sleep

import hashlib
import random
import string
import json

servico = Flask(__name__)

PROCESS = "didadic_material"
DESCRIPTION = "Didactic material review and release service"
VERSION = "0.0.1"


def start():
    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1))
    cliente.add_topic(PROCESS)
    cliente.close()


@servico.route("/info", methods=["GET"])
def get_info():
    return jsonify(descricao=DESCRIPTION, versao=VERSION)


@servico.route("/executar/<int:id_reviewer>/<int:id_material>", methods=["POST", "GET"])
def executar(id_reviewer, id_material):
    response = {
        "result": "success",
        "id_revision": ""
    }

    # simula algum processamento atraves de espera ocupada
    #sleep(4)

    ID = "".join(random.choice(string.ascii_letters +
                               string.punctuation) for _ in range(12))
    ID = hashlib.md5(ID.encode("utf-8")).hexdigest()

    try:
        produtor = KafkaProducer(
            bootstrap_servers=["kafka:29092"],
            api_version=(0, 10, 1))

        revision = {
            "id_revision": ID,
            "success": 1,
            "message": "Novo material a ser revisado.",
            "created_at": "",
            "id_revisor": id_reviewer,
            "id_material": id_material
        }
        produtor.send(topic=PROCESS, value=json.dumps(
            revision).encode("utf-8"))

        response["id_revision"] = revision["id_revision"]
    except KafkaError as erro:
        response["resultado"] = f"An error occurred during revision initialization: {erro}"

    return json.dumps(response).encode("utf-8")


if __name__ == "__main__":
    start()

    servico.run(
        host="0.0.0.0",
        debug=True
    )

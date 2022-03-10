import datetime
import logging
import os

import boto3
from qiskit import IBMQ
from qiskit import QuantumCircuit, execute

logger = logging.getLogger()
logger.setLevel(logging.INFO)

backend_candidates = [
    "ibmq_bogota",
    "ibmq_quito",
    "ibmq_belem",
    "ibmq_lima",
    "ibmq_manila",
    "ibmq_santiago",
]


def _get_provider():
    if IBMQ.active_account() is None:
        ibmq_token = os.environ["IBMQ_TOKEN"]
        provider = IBMQ.enable_account(ibmq_token)
    else:
        provider = IBMQ.get_provider(hub="ibm-q", group="open", project="main")

    return provider


def execute_circuit(event: dict, context) -> dict:
    provider = _get_provider()
    devices = provider.backends(
        filters=lambda x: x.configuration().n_qubits >= 4
        and not x.configuration().simulator
        and x.status().status_msg == "active"
    )
    logger.info(f"active backend={devices}")

    backend_name = None
    for backend_candidate in backend_candidates:
        for device in devices:
            if backend_candidate == device.name():
                backend_name = device.name()
                break
        if backend_name is not None:
            break

    if backend_name is None:
        message = f"active backend is not found in {backend_candidates}. can not execute circuit."
        logger.error(message)
        raise Exception(message)
    else:
        logger.info(f"use backend={backend_name}")

    # build quantum circuit
    circuit = QuantumCircuit(4, 4)
    circuit.h([0, 1, 2, 3])
    circuit.measure([0, 1, 2, 3], [0, 1, 2, 3])

    # execute
    backend = provider.get_backend(backend_name)
    job = execute(circuit, backend)
    job_id = job.job_id()

    response = {"backend_name": backend_name, "job_id": job_id}
    logger.info(f"response={response}")
    return response


def get_job_status(event: dict, context) -> dict:
    logger.info(f"event={event}")

    # get job status
    provider = _get_provider()
    job = provider.get_backend(event["backend_name"]).retrieve_job(event["job_id"])
    logger.info(f"job={job}")

    response = {
        "backend_name": event["backend_name"],
        "job_id": event["job_id"],
        "job_status": job.status().name,
    }
    logger.info(f"response={response}")
    return response


def store_result(event: dict, context) -> dict:
    logger.info(f"event={event}")

    # get job result
    provider = _get_provider()
    job = provider.get_backend(event["backend_name"]).retrieve_job(event["job_id"])
    counts = job.result().get_counts()
    result = dict([("num_of_" + key, value) for key, value in counts.items()])
    result["id"] = "latest"
    result["backend_name"] = event["backend_name"]
    result["job_id"] = event["job_id"]
    result["creation_date"] = job.creation_date().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # result["creation_date"] = job.creation_date()

    # store the execution result to DynamoDB
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ["DYNAMODB_TABLE"]
    table = dynamodb.Table(table_name)
    # store latest record
    table.put_item(Item=result)
    # store history record
    # dt = datetime.datetime.strptime(result["creation_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
    # result["id"] = dt.strftime("%Y%m%d-%H%M%S")  # UTC
    result["id"] = job.creation_date().strftime("%Y%m%d-%H%M%S")  # UTC
    table.put_item(Item=result)

    logger.info(f"result={result}")
    return result


def invoke_update_horoscope(event: dict, context) -> dict:
    logger.info(f"event={event}")
    sfn = boto3.client("stepfunctions")
    result = None

    # get the arn of UpdateHoroscope Step Functions
    state_machine_list = sfn.list_state_machines()
    for state_machine in state_machine_list["stateMachines"]:
        name = state_machine["name"]
        if name == f"UpdateHoroscope-{os.environ['STAGE']}":
            # execute UpdateHoroscope Step Functions
            arn = state_machine["stateMachineArn"]
            sfn.start_execution(stateMachineArn=arn)
            result = {"name": name, "arn": arn}
            logger.info(f"sfn.start_execution: result={result}")
            break

    return result

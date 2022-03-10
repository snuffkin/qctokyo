from decimal import Decimal
import json
from logging import INFO, ERROR
import os
import requests_mock

import boto3
from moto import mock_dynamodb2, mock_stepfunctions
import pytest

from .fake_provider import FakeProviderFactory

import qiskit
from qiskit.providers.jobstatus import JobStatus
from qiskit.test.mock.fake_job import FakeJob
from qiskit.test.mock.fake_provider import FakeProvider
from qiskit.test.mock.backends import FakeOurense

qiskit.IBMQ = FakeProviderFactory()

from qctokyo import horoscope


def setup_module(module):
    os.environ["STAGE"] = "dev"
    os.environ["DYNAMODB_TABLE"] = "horoscope-dev"


def teardown_module(module):
    del os.environ["STAGE"]
    del os.environ["DYNAMODB_TABLE"]


def test_execute_circuit(caplog):
    # execution
    actual = horoscope.execute_circuit(None, None)

    # validate return value
    assert actual["backend_name"] == "ibmq_bogota"
    assert actual["job_id"] != None

    # validate logger
    assert caplog.record_tuples[1] == ("root", INFO, "use backend=ibmq_bogota")
    assert caplog.record_tuples[-1][0] == "root"
    assert caplog.record_tuples[-1][1] == INFO
    assert caplog.record_tuples[-1][2].startswith(
        "response={'backend_name': 'ibmq_bogota', 'job_id'"
    )


def test_execute_circuit_backend_not_found(mocker, caplog):
    mocker.patch.object(FakeProvider, "backends", return_value=[])

    # execution
    with pytest.raises(Exception) as excinfo:
        horoscope.execute_circuit(None, None)

    # validate exceeption
    assert excinfo.value.args == (
        "active backend is not found in ['ibmq_bogota', 'ibmq_quito', 'ibmq_belem', 'ibmq_lima', 'ibmq_manila', 'ibmq_santiago']. can not execute circuit.",
    )

    # validate logger
    assert caplog.record_tuples[0] == ("root", INFO, "active backend=[]")
    assert caplog.record_tuples[1] == (
        "root",
        ERROR,
        "active backend is not found in ['ibmq_bogota', 'ibmq_quito', 'ibmq_belem', 'ibmq_lima', 'ibmq_manila', 'ibmq_santiago']. can not execute circuit.",
    )


def test_get_job_status(mocker):
    def mock_status():
        return JobStatus.DONE

    def mock_retrieve_job(job_id: str):
        job = FakeJob(None, job_id, None)
        job.status = mock_status
        return job

    mock_backend = FakeOurense()
    mock_backend.retrieve_job = mock_retrieve_job

    mocker.patch.object(
        FakeProvider, "get_backend", return_value=mock_backend, create=True
    )

    event = {
        "backend_name": "ibmq_ourense",
        "job_id": "dummy_job_id",
    }

    # execution
    actual = horoscope.get_job_status(event, None)

    # validate return value
    assert actual["backend_name"] == "ibmq_ourense"
    assert actual["job_id"] == "dummy_job_id"
    assert actual["job_status"] == "DONE"


@pytest.mark.skip
@mock_dynamodb2
def test_store_result(mocker):
    def mock_get_count():
        return {
            "0000": 100,
            "0001": 101,
            "0010": 102,
            "0011": 103,
            "0100": 104,
            "0101": 105,
            "0110": 106,
            "0111": 107,
            "1000": 108,
            "1001": 109,
            "1010": 110,
            "1011": 111,
            "1100": 112,
            "1101": 113,
            "1110": 114,
            "1111": 115,
        }

    def mock_creation_date():
        return "2019-07-01T00:01:02.345000Z"

    def mock_result():  # TODO
        result = mocker.Mock()
        result.get_counts = mock_get_count
        return result

    def mock_retrieve_job(job_id: str):
        job = FakeJob(None, job_id, None)
        job.creation_date = mock_creation_date
        job.result = mock_result
        return job

    mock_backend = FakeOurense()
    mock_backend.retrieve_job = mock_retrieve_job

    mocker.patch.object(
        FakeProvider, "get_backend", return_value=mock_backend, create=True
    )

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.create_table(
        TableName=os.environ["DYNAMODB_TABLE"],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
    )

    event = {
        "backend_name": "ibmq_ourense",
        "job_id": "dummy_job_id",
    }

    # execution
    actual = horoscope.store_result(event, None)

    # validate return value
    expected = {
        "id": "20190701-000102",
        "backend_name": "ibmq_ourense",
        "job_id": "dummy_job_id",
        "creation_date": "2019-07-01T00:01:02.345000Z",
        "num_of_0000": 100,
        "num_of_0001": 101,
        "num_of_0010": 102,
        "num_of_0011": 103,
        "num_of_0100": 104,
        "num_of_0101": 105,
        "num_of_0110": 106,
        "num_of_0111": 107,
        "num_of_1000": 108,
        "num_of_1001": 109,
        "num_of_1010": 110,
        "num_of_1011": 111,
        "num_of_1100": 112,
        "num_of_1101": 113,
        "num_of_1110": 114,
        "num_of_1111": 115,
    }
    assert actual == expected

    # validate DynamoDB
    expected_item = {
        "id": "latest",
        "backend_name": "ibmq_ourense",
        "job_id": "dummy_job_id",
        "creation_date": "2019-07-01T00:01:02.345000Z",
        "num_of_0000": Decimal("100"),
        "num_of_0001": Decimal("101"),
        "num_of_0010": Decimal("102"),
        "num_of_0011": Decimal("103"),
        "num_of_0100": Decimal("104"),
        "num_of_0101": Decimal("105"),
        "num_of_0110": Decimal("106"),
        "num_of_0111": Decimal("107"),
        "num_of_1000": Decimal("108"),
        "num_of_1001": Decimal("109"),
        "num_of_1010": Decimal("110"),
        "num_of_1011": Decimal("111"),
        "num_of_1100": Decimal("112"),
        "num_of_1101": Decimal("113"),
        "num_of_1110": Decimal("114"),
        "num_of_1111": Decimal("115"),
    }
    response = table.scan()
    assert response["Count"] == 2
    assert response["Items"][0] == expected_item
    expected_item["id"] = "20190701-000102"
    assert response["Items"][1] == expected_item


@mock_stepfunctions
def test_invoke_update_horoscope():
    sfn = boto3.client("stepfunctions")
    sfn.create_state_machine(
        name="dummy-sfn",
        definition="dummy_definition",
        roleArn="arn:aws:iam::123456789012:role/qctokyo-apps-dev-IamRoleStateMachineExecution-dummy",
    )
    sfn.create_state_machine(
        name="UpdateHoroscope-dev",
        definition="dummy_definition",
        roleArn="arn:aws:iam::123456789012:role/qctokyo-apps-dev-IamRoleStateMachineExecution",
    )

    event = {
        "backend_name": "ibmq_ourense",
        "job_id": "dummy_job_id",
    }

    # execution
    actual = horoscope.invoke_update_horoscope(event, None)

    # validate return value
    assert actual["name"] == "UpdateHoroscope-dev"
    assert (
        actual["arn"]
        == "arn:aws:states:us-west-2:123456789012:stateMachine:UpdateHoroscope-dev"
    )

    # validate Step Functions
    executions = sfn.list_executions(
        stateMachineArn="arn:aws:states:us-west-2:123456789012:stateMachine:UpdateHoroscope-dev"
    )
    assert len(executions["executions"]) == 1
    assert executions["executions"][0]["status"] == "RUNNING"

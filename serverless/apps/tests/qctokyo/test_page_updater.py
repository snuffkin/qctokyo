import json
from logging import INFO
import os
import requests_mock

import boto3
from moto import mock_dynamodb2, mock_s3
import pytest

from qctokyo import page_updater


def setup_module(module):
    os.environ["S3_BUCKET_NAME"] = "www-dev.quantumcomputer.tokyo"
    os.environ["S3_TEMPLATE_KEY"] = "horoscope_template.html"
    os.environ["S3_OUTPUT_KEY"] = "horoscope.html"
    os.environ["DYNAMODB_TABLE"] = "horoscope-dev"


def teardown_module(module):
    del os.environ["S3_BUCKET_NAME"]
    del os.environ["S3_TEMPLATE_KEY"]
    del os.environ["S3_OUTPUT_KEY"]
    del os.environ["DYNAMODB_TABLE"]


@pytest.mark.skip
@mock_s3
def test_update_page():
    # setup S3
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(os.environ["S3_BUCKET_NAME"])
    bucket.create(
        CreateBucketConfiguration={
            "LocationConstraint": os.environ["AWS_DEFAULT_REGION"]
        }
    )

    with open(
        os.path.join(
            os.path.dirname(__file__), "../../../static/horoscope_template.html"
        )
    ) as f:
        html_template = f.read()
    bucket.Object(os.environ["S3_TEMPLATE_KEY"]).put(Body=html_template)

    with open(
        os.path.join(os.path.dirname(__file__), "../../../static/horoscope.html")
    ) as f:
        html = f.read()
    bucket.Object(os.environ["S3_OUTPUT_KEY"]).put(Body=html)

    # setup DynamoDB
    with mock_dynamodb2():
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.create_table(
            TableName=os.environ["DYNAMODB_TABLE"],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        )
        record = {
            "id": "latest",
            "job_id": "dummy_job_id",
            "backend_name": "dummy_backend_name",
            "creation_date": "2019-07-01T00:01:02.123456Z",
            "num_of_0000": 10,
            "num_of_0001": 9,
            "num_of_0010": 8,
            "num_of_0011": 7,
            "num_of_0100": 6,
            "num_of_0101": 5,
            "num_of_0110": 4,
            "num_of_0111": 3,
            "num_of_1000": 2,
            "num_of_1001": 1,
            "num_of_1010": 16,
            "num_of_1011": 15,
            "num_of_1100": 14,
            "num_of_1101": 13,
            "num_of_1110": 12,
            "num_of_1111": 11,
        }
        table.put_item(Item=record)

        # execution
        actual = page_updater.update_page(None, None)

    # validate return value
    expected = {
        "backend_name": "dummy_backend_name",
        "creation_date": "2019-07-01 00:01",
        "rank1": "<td>Aquarius</td><td>Jan 20 - Feb 18</td>",
        "rank2": "<td>Pisces</td><td>Feb 19 - Mar 20</td>",
        "rank3": "<td>Aries</td><td>Mar 21 - Apr 19</td>",
        "rank4": "<td>Taurus</td><td>Apr 20 - May 20</td>",
        "rank5": "<td>Gemini</td><td>May 21 - Jun 20</td>",
        "rank6": "<td>Cancer</td><td>Jun 21 - Jul 22</td>",
        "rank7": "<td>Leo</td><td>Jul 23 - Aug 22</td>",
        "rank8": "<td>Virgo</td><td>Aug 23 - Sep 22</td>",
        "rank9": "<td>Libra</td><td>Sep 23 - Oct 22</td>",
        "rank10": "<td>Scorpio</td><td>Oct 23 - Nov 21</td>",
        "rank11": "<td>Sagittarius</td><td>Nov 22 - Dec 21</td>",
        "rank12": "<td>Capricorn</td><td>Dec 22 -Jan 19</td>",
    }
    assert actual == expected

    # validate S3
    actual_html = (
        bucket.Object(os.environ["S3_OUTPUT_KEY"]).get()["Body"].read().decode("utf-8")
    )
    with open(os.path.join(os.path.dirname(__file__), "horoscope_expected.html")) as f:
        expected_html = f.read()
    assert actual_html == expected_html

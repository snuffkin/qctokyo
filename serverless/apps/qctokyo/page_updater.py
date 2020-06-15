import logging
import os
from string import Template

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# mapping column names of DynamoDB to the html elements of zodiac
COLUMN_TO_ZODIAC = {
    "num_of_0000": "<td>Aries</td><td>Mar 21 - Apr 19</td>",
    "num_of_0001": "<td>Taurus</td><td>Apr 20 - May 20</td>",
    "num_of_0010": "<td>Gemini</td><td>May 21 - Jun 20</td>",
    "num_of_0011": "<td>Cancer</td><td>Jun 21 - Jul 22</td>",
    "num_of_0100": "<td>Leo</td><td>Jul 23 - Aug 22</td>",
    "num_of_0101": "<td>Virgo</td><td>Aug 23 - Sep 22</td>",
    "num_of_0110": "<td>Libra</td><td>Sep 23 - Oct 22</td>",
    "num_of_0111": "<td>Scorpio</td><td>Oct 23 - Nov 21</td>",
    "num_of_1000": "<td>Sagittarius</td><td>Nov 22 - Dec 21</td>",
    "num_of_1001": "<td>Capricorn</td><td>Dec 22 -Jan 19</td>",
    "num_of_1010": "<td>Aquarius</td><td>Jan 20 - Feb 18</td>",
    "num_of_1011": "<td>Pisces</td><td>Feb 19 - Mar 20</td>",
}


def update_page(event: dict, context) -> dict:
    # get the HTML template from S3
    s3 = boto3.client("s3")
    bucket_name = os.environ["S3_BUCKET_NAME"]
    template_key = os.environ["S3_TEMPLATE_KEY"]
    output_key = os.environ["S3_OUTPUT_KEY"]
    s3_response = s3.get_object(Bucket=bucket_name, Key=template_key)
    template = s3_response["Body"].read().decode("utf-8")

    # get the latest execution result from DynamoDB
    dynamodb = boto3.client("dynamodb")
    table_name = os.environ["DYNAMODB_TABLE"]
    dynamodb_response = dynamodb.get_item(
        TableName=table_name, Key={"id": {"S": "latest"}}
    )
    item = dynamodb_response["Item"]
    logger.info(f"item={item}")

    # put the result in the template
    # since the result contain information from 0000-1111, filter the result to 0000-1100
    filtered_result = {
        k: int(v["N"])
        for k, v in item.items()
        if k.startswith("num_of_") and int(k[7:], 2) < 12
    }
    sorted_result = sorted(filtered_result.items(), key=lambda x: x[1], reverse=True)
    result = {
        f"rank{i+1}": COLUMN_TO_ZODIAC[k] for i, (k, v) in enumerate(sorted_result)
    }
    creation_date = item["creation_date"]["S"]
    creation_date = creation_date[:16].replace("T", " ")
    result["creation_date"] = creation_date
    result["backend_name"] = item["backend_name"]["S"]
    logger.info(f"result={result}")

    output = Template(template).substitute(**result)

    # put HTML to S3
    s3.put_object(
        Bucket=bucket_name, Key=output_key, Body=output, ContentType="text/html"
    )
    return result

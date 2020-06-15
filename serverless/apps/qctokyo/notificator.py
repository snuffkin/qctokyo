import json
import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def notify_horoscope_success_to_slack(event: dict, context) -> dict:
    logger.info(f"event={event}")
    title = "storing horoscope is success:smile:"
    messages = [
        f"job_id: {event['job_id']}",
        f"backend_name: {event['backend_name']}",
        f"creation_date: {event['creation_date']} UTC",
    ]

    _post_slack(title, "good", "\n".join(messages))
    return event


def notify_horoscope_failed_to_slack(event: dict, context) -> dict:
    logger.info(f"event={event}")
    title = "storing horoscope is failure:rage:"
    messages = ["Check detail!"]
    if "detail" in event and "status" in event["detail"]:
        messages.append(f'status: {event["detail"]["status"]}')

    _post_slack(title, "danger", "\n".join(messages))
    return event


def notify_horoscope_update_to_slack(event: dict, context) -> dict:
    logger.info(f"event={event}")
    title = "updating horoscope is success:smile:"
    filtered_result = {int(k[4:]): v for k, v in event.items() if k.startswith("rank")}
    sorted_result = sorted(filtered_result.items(), key=lambda x: x[0])
    result = [
        str(x[0])
        + ": "
        + x[1]
        .replace(" ", "")
        .replace("</td><td>", ", ")
        .replace("<td>", "")
        .replace("</td>", "")
        for x in sorted_result
    ]

    messages = [f"received new oracle at {event['creation_date']} UTC"]
    messages.extend(result)
    messages.append("https://www.quantumcomputer.tokyo/horoscope.html")

    _post_slack(title, "good", "\n".join(messages))
    return event


def notify_horoscope_update_failed_to_slack(event: dict, context) -> dict:
    logger.info(f"event={event}")
    title = "updating horoscope is failure:rage:"
    messages = ["Check detail!"]
    if "detail" in event and "status" in event["detail"]:
        messages.append(f'status: {event["detail"]["status"]}')

    _post_slack(title, "danger", "\n".join(messages))
    return event


def _post_slack(title: str, color: str, detail: str) -> None:
    payload = {
        "attachments": [
            {
                "color": color,
                "pretext": f"[{os.environ['STAGE']}] {title}",
                "text": detail,
            }
        ]
    }

    try:
        slack_webhook_url = "https://" + os.environ["SLACK_WEBHOOK_URL"]
        response = requests.post(slack_webhook_url, data=json.dumps(payload))
    except requests.exceptions.RequestException:
        logger.exception(f"failed to call slack_webhook")
    else:
        logger.info(f"slack_webhook_response status_code={response.status_code}")

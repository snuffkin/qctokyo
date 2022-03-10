import json
from logging import INFO, ERROR
import os

import requests
import requests_mock
import pytest

from qctokyo import notificator


def setup_module(module):
    os.environ["STAGE"] = "dev"
    os.environ["SLACK_WEBHOOK_URL"] = "hooks.slack.com/services/dummy"


def teardown_module(module):
    del os.environ["STAGE"]
    del os.environ["SLACK_WEBHOOK_URL"]


@pytest.mark.skip
def test_notify_horoscope_success_to_slack(caplog):
    event = {
        "job_id": "dummy_job_id",
        "backend_name": "dummy_backend_name",
        "creation_date": "2019-07-01T00:01:02.123456Z",
    }
    context = None

    with requests_mock.Mocker() as m:
        m.post("https://hooks.slack.com/services/dummy")

        # execution
        actual = notificator.notify_horoscope_success_to_slack(event, context)

    # validate return value
    assert actual == event
    assert m.call_count == 1
    attachments = json.loads(m.request_history[0].text)["attachments"]
    assert len(attachments) == 1
    attachment0 = attachments[0]
    assert attachment0["color"] == "good"
    assert attachment0["pretext"] == "[dev] storing horoscope is success:smile:"
    assert (
        attachment0["text"]
        == "job_id: dummy_job_id\nbackend_name: dummy_backend_name\ncreation_date: 2019-07-01T00:01:02.123456Z UTC"
    )

    # validate logger
    assert caplog.record_tuples[1] == (
        "root",
        INFO,
        "slack_webhook_response status_code=200",
    )


@pytest.mark.skip
def test_notify_horoscope_failed_to_slack(caplog):
    event = {
        "job_id": "dummy_job_id",
        "backend_name": "dummy_backend_name",
        "creation_date": "2019-07-01T00:01:02.123456Z",
        "detail": {"status": "FAILED"},
    }
    context = None

    with requests_mock.Mocker() as m:
        m.post("https://hooks.slack.com/services/dummy")

        # execution
        actual = notificator.notify_horoscope_failed_to_slack(event, context)

    # validate return value
    assert actual == event
    assert m.call_count == 1
    attachments = json.loads(m.request_history[0].text)["attachments"]
    assert len(attachments) == 1
    attachment0 = attachments[0]
    assert attachment0["color"] == "danger"
    assert attachment0["pretext"] == "[dev] storing horoscope is failure:rage:"
    assert attachment0["text"] == "Check detail!\nstatus: FAILED"

    # validate logger
    assert caplog.record_tuples[1] == (
        "root",
        INFO,
        "slack_webhook_response status_code=200",
    )


@pytest.mark.skip
def test_notify_horoscope_update_to_slack(caplog):
    event = {
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
        "backend_name": "dummy_backend_name",
        "creation_date": "2019-07-01 00:01",
    }
    context = None

    with requests_mock.Mocker() as m:
        m.post("https://hooks.slack.com/services/dummy")

        # execution
        actual = notificator.notify_horoscope_update_to_slack(event, context)

    # validate return value
    assert actual == event
    assert m.call_count == 1
    attachments = json.loads(m.request_history[0].text)["attachments"]
    assert len(attachments) == 1
    attachment0 = attachments[0]
    assert attachment0["color"] == "good"
    assert attachment0["pretext"] == "[dev] updating horoscope is success:smile:"
    expected_text = "\n".join(
        [
            "received new oracle at 2019-07-01 00:01 UTC",
            "1: Aquarius, Jan20-Feb18",
            "2: Pisces, Feb19-Mar20",
            "3: Aries, Mar21-Apr19",
            "4: Taurus, Apr20-May20",
            "5: Gemini, May21-Jun20",
            "6: Cancer, Jun21-Jul22",
            "7: Leo, Jul23-Aug22",
            "8: Virgo, Aug23-Sep22",
            "9: Libra, Sep23-Oct22",
            "10: Scorpio, Oct23-Nov21",
            "11: Sagittarius, Nov22-Dec21",
            "12: Capricorn, Dec22-Jan19",
            "https://www.quantumcomputer.tokyo/horoscope.html",
        ]
    )
    assert attachment0["text"] == expected_text

    # validate logger
    assert caplog.record_tuples[1] == (
        "root",
        INFO,
        "slack_webhook_response status_code=200",
    )


@pytest.mark.skip
def test_notify_horoscope_update_failed_to_slack(caplog):
    event = {
        "job_id": "dummy_job_id",
        "backend_name": "dummy_backend_name",
        "creation_date": "2019-07-01T00:01:02.123456Z",
        "detail": {"status": "FAILED"},
    }
    context = None

    with requests_mock.Mocker() as m:
        m.post("https://hooks.slack.com/services/dummy")

        # execution
        actual = notificator.notify_horoscope_update_failed_to_slack(event, context)

    # validate return value
    assert actual == event
    assert m.call_count == 1
    attachments = json.loads(m.request_history[0].text)["attachments"]
    assert len(attachments) == 1
    attachment0 = attachments[0]
    assert attachment0["color"] == "danger"
    assert attachment0["pretext"] == "[dev] updating horoscope is failure:rage:"
    assert attachment0["text"] == "Check detail!\nstatus: FAILED"

    # validate logger
    assert caplog.record_tuples[1] == (
        "root",
        INFO,
        "slack_webhook_response status_code=200",
    )


@pytest.mark.skip
def test_post_slack(caplog):
    with requests_mock.Mocker() as m:
        m.post("https://hooks.slack.com/services/dummy")
        title = "updating horoscope is success:smile:"
        color = "good"
        detail = "test message"

        # execution
        notificator._post_slack(title, color, detail)

    # validate return value
    assert m.call_count == 1
    attachments = json.loads(m.request_history[0].text)["attachments"]
    assert len(attachments) == 1
    attachment0 = attachments[0]
    assert attachment0["color"] == "good"
    assert attachment0["pretext"] == "[dev] updating horoscope is success:smile:"
    assert attachment0["text"] == "test message"

    # validate logger
    assert caplog.record_tuples == [
        ("root", INFO, "slack_webhook_response status_code=200"),
    ]


@pytest.mark.skip
def test_post_slack_exception(mocker, caplog):
    mocker.patch.object(
        requests,
        "post",
        side_effect=requests.exceptions.RequestException("test exception"),
    )

    title = "updating horoscope is success:smile:"
    color = "good"
    detail = "test message"

    # execution
    notificator._post_slack(title, color, detail)

    # validate logger
    assert caplog.record_tuples == [
        ("root", ERROR, "failed to call slack_webhook"),
    ]

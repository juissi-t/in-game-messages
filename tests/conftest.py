import json
import pytest


@pytest.fixture
def message_with_reply():
    json_message = """
{
    "sourceid": 374955,
    "sourcename": "Leshy Sector",
    "sourcetype": 2,
    "targetid": 374955,
    "targetname": "Leshy Sector",
    "targettype": 2,
    "gameid": 374955,
    "gamename": "Leshy Sector",
    "message": "pysh has been dropped from The Horwasp Plague after missing three turns.",
    "dateadded": "2020-06-12T04:02:08",
    "turn": 4,
    "activitytype": 10,
    "reference": null,
    "attachment": null,
    "scope": 2,
    "parentid": 0,
    "orderid": 637275375741751700,
    "replycount": 1,
    "likecount": 0,
    "likeid": 0,
    "likename": null,
    "_replies": [
        {
            "sourceid": 16802,
            "sourcename": "coen1970 (The Colonies)",
            "sourcetype": 1,
            "targetid": 0,
            "targetname": null,
            "targettype": 0,
            "gameid": 374955,
            "gamename": "Leshy Sector",
            "message": "One down, two to go :)",
            "dateadded": "2020-06-12T05:46:14",
            "turn": 5,
            "activitytype": 1,
            "reference": null,
            "attachment": null,
            "scope": 2,
            "parentid": 4800541,
            "orderid": 637275436959671900,
            "replycount": 1,
            "likecount": 1,
            "likeid": 5195,
            "likename": "cyberian",
            "_replies": null,
            "id": 4800693
        }
    ],
    "id": 4800541
}
    """
    return json.loads(json_message)


@pytest.fixture
def message_no_replies():
    json_message = """
{
    "sourceid": 5635,
    "sourcename": "tom n (The Lizards)",
    "sourcetype": 1,
    "targetid": 16802,
    "targetname": "coen1970 (The Colonies)",
    "targettype": 1,
    "gameid": 374955,
    "gamename": "Leshy Sector",
    "message": "Hi Coen,<br/><br/>Early message this time. My Bohemian will head due south and arrive at (2457, 2276) next turn. Please advice if I need to set FC to match any mine fields, etc.<br/><br/>Thanks!  Tom N",
    "dateadded": "2020-07-06T04:17:23",
    "turn": 21,
    "activitytype": 1,
    "reference": null,
    "attachment": null,
    "scope": 3,
    "parentid": 0,
    "orderid": 637296058433225700,
    "replycount": 0,
    "likecount": 0,
    "likeid": 0,
    "likename": null,
    "_replies": [],
    "id": 4847926
}
    """
    return json.loads(json_message)

import os, sys
import requests
from twilio.rest import Client as twilio_client
from datetime import datetime

try:
    sid = os.environ['TWILIO_SID']
    token = os.environ['TWILIO_TOKEN']
    client = twilio_client(sid, token)

    # help(client.messages.list)
    messages = client.messages.list(date_sent_after=datetime(2020, 2, 1),
                                    date_sent_before=datetime(2020, 2, 2))

    for rec in messages:
        print('From: {}, To: {}, Status: {}, Price: {}'.format(
            rec.from_, rec.to, rec.status, rec.price))
except NoKeyError as e:
    pass

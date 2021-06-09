import sys

import sys
import json
import time
import datetime, pytz

from FAZAPIWrapper import *

from st2common.runners.base_action import Action

from st2client.client import Client
from st2client.models import KeyValuePair

timezone = pytz.timezone("Europe/Minsk")

class AckAlert(Action):

    def run(self, adom, alerts, comment):

        apiw = FAZAPIWrapper()
        login_res = apiw.login(self.config['faz_ip'], self.config['username'], self.config['password'])

        if not alerts:
            client = Client(base_url='http://localhost')
            alerts = client.keys.get_by_name(name='cached_alerts').value

        if login_res[0]['status']['code'] == 0:

            alerts = json.loads(alerts)

            if len(alerts) > 0:

                comment_str = ""
                now_in_tz = datetime.datetime.now().astimezone(timezone)
                if comment:
                    comment_str = "%s; t: %s" % (comment, now_in_tz)

                for alert in alerts:
                    if comment_str:
                        apiw.set_alert_comment(adom, alert['alertid'], comment_str)
                    apiw.set_alert_acknowledged(adom, alert['alertid'])

                apiw.logout()
                return(True, "Ack: ok!")

        return (False, "Log in failed, %s" % login_res)

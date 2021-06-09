import sys

import sys
import json
import time
import datetime

from FAZAPIWrapper import *

from st2common.runners.base_action import Action

from st2client.client import Client
from st2client.models import KeyValuePair

class GetNewAlertsAction(Action):
    def run(self, adom, alert_handler_name, event_handler_period, max_alert_age, limit, euname):

        apiw = FAZAPIWrapper()
        login_res = apiw.login(self.config['faz_ip'], self.config['username'], self.config['password'])

        if login_res[0]['status']['code'] == 0:
            alerts = apiw.get_new_alerts(adom, alert_handler_name, event_handler_period, max_alert_age, limit, euname)
            apiw.logout()

            if alerts:

                # fix missing euname
                for alert in alerts['data']:
                    if 'euname' not in alert:
                        alert['euname'] = 'N/A'

                client = Client(base_url='http://localhost')
                client.keys.update(KeyValuePair(name='cached_alerts', value=json.dumps(alerts['data'])))

                return (True, alerts)
        return (False, "Log in failed, %s" % login_res)

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

            alerts_dict = {}

            if alerts:
                for alert in alerts['data']:
                    # fix missing euname
                    if 'euname' not in alert:
                        alert['euname'] = 'N/A'
                    if not alert['euname']:
                        alert['euname'] = 'N/A'
                #
                #     id = alert['euname']
                #     if id not in alerts_dict:
                #         alerts_dict[id] = []
                #
                #     alerts_dict[id].append(alert)
                #
                # cached_alerts_by_user_list = []
                # cached_alerts_user_na_list = []
                # for key in alerts_dict.keys():
                #     if key == 'N/A':
                #         cached_alerts_user_na_list.append(alerts_dict[key])
                #     else:
                #         cached_alerts_by_user_list.append(alerts_dict[key])

                client = Client(base_url='http://localhost')
                client.keys.update(KeyValuePair(name='cached_alerts', value=json.dumps(alerts['data'])))
                # client.keys.update(KeyValuePair(name='cached_alerts_by_user', value=json.dumps({ 'data': cached_alerts_by_user_list })))
                # client.keys.update(KeyValuePair(name='cached_alerts_user_na', value=json.dumps({ 'data': cached_alerts_user_na_list })))

                return (True, alerts)
        return (False, "Log in failed, %s" % login_res)

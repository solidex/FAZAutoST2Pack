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

class RunReport(Action):

    def run(self, adom, email_to_address, report_id, user_id, alerts, ack, comment):

        apiw = FAZAPIWrapper()
        login_res = apiw.login(self.config['faz_ip'], self.config['username'], self.config['password'])

        output_format = self.config['output_format'].split(',')

        if not alerts:
            client = Client(base_url='http://localhost')
            alerts = client.keys.get_by_name(name='cached_alerts').value

        if login_res[0]['status']['code'] == 0:
            alerts = json.loads(alerts)
            if len(alerts) == 0:
                return(False, '`alerts` parameter is emply!')

            filtered_alerts = []
            for alert in alerts:
                if alert['euname'] == user_id:
                    filtered_alerts.append(alert)

            alerts = filtered_alerts # ! working with filtered alerts

            if len(alerts) > 0:

                euname = user_id

                output_profile_name = euname.replace('.', '_')

                apiw.create_output_profile(adom, output_profile_name)
                upd_out_prof_rslt = apiw.update_output_profile(adom, output_profile_name,
                    self.config['server_name'], self.config['email_from_address'],
                    email_to_address, self.config['email_subject'],
                    output_format)
                if not upd_out_prof_rslt:
                    return (False, "Update output profile error")
                if upd_out_prof_rslt['status']['code'] != 0:
                    return (False, "Update output profile non-zero code, %s" % upd_out_prof_rslt)

                alerttime = datetime.datetime.fromtimestamp(int(alerts[0]['alerttime']))
                lastlogtime = datetime.datetime.fromtimestamp(int(alerts[0]['lastlogtime']))

                for alert in alerts:
                    _alerttime = datetime.datetime.fromtimestamp(int(alert['alerttime']))
                    _lastlogtime = datetime.datetime.fromtimestamp(int(alert['lastlogtime']))
                    if _alerttime < alerttime:
                        alerttime = _alerttime
                    if _lastlogtime > lastlogtime:
                        lastlogtime = _lastlogtime

                apiw.config_report(adom, report_id, alerttime.astimezone(timezone),
                    lastlogtime.astimezone(timezone), "", euname, output_profile_name)
                tid = apiw.run_report(adom, report_id)['tid']
                #
                report_name = "n/a"
                while True:

                    status = apiw.get_report_status(adom, tid)
                    if status:
                        if status['progress-percent'] == 100:
                            report_name = status['name']
                            break
                    time.sleep(3)

                now_in_tz = datetime.datetime.now().astimezone(timezone)
                comment_str = "report_id: %s; report_name: %s; sent_to: %s; t: %s" % (tid, report_name, email_to_address, now_in_tz)
                for alert in alerts:
                    if comment:
                        apiw.set_alert_comment(adom, alert['alertid'], comment_str)
                    if ack:
                        apiw.set_alert_acknowledged(adom, alert['alertid'])

                apiw.logout()
                return(True, comment_str)
            else:
                return(False, 'Alert list doesn\'t have any alerts for `%s`' % user_id)

        return (False, "Log in failed, %s" % login_res)

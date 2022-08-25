import sys
import json
import time
import datetime, pytz

from st2common.runners.base_action import Action

from FAZAPIWrapper import *

timezone = pytz.timezone("Europe/Minsk")




class AckAlert(Action):

    def run(self, adom, user_id, alerts, comment):
        #
        # get list of alerts to be acknowledged
        if not alerts:
            self.logger.debug("function arg alerts={}, querying st2-datastore for cached alerts".format(alerts))
            alerts = self.action_service.get_value('cached_alerts')
        try:
            alerts = json.loads(alerts)
        except: 
            self.logger.exception("Failed to extract alerts from JSON: {}".format(alerts))
            return(False, 'Alerts cannot be extracted for {}'.format(user_id))
        #
        self.logger.info("Found {} alerts to be acknowledged".format(len(alerts)))
        #
        # connect to FMG
        apiw = FAZAPIWrapper()
        self.logger.debug("Trying connect to FortiManager: {}:{}@{}".format(
                                                                self.config['username'], 
                                                                self.config['faz_ip'],
                                                                self.config['password'][:2] + 8 * "*",
                                                                ))
        login_res = apiw.login(self.config['faz_ip'], self.config['username'], self.config['password'])
        #
        if login_res[0]['status']['code'] == 0:
            self.logger.info("Successfully connected to FortiManager!")
            #
            if len(alerts) == 0:
                return(False, '`alerts` parameter is emply!')
            #
            filtered_alerts = []
            for alert in alerts:
                if alert['euname'] == user_id:
                    filtered_alerts.append(alert)

            self.logger.info("{} alerts have been removed from results due to filter user_id={}".format(
                                len(alerts) - len(filtered_alerts), user_id))
            #
            alerts = filtered_alerts
            if len(alerts) > 0:

                comment_str = ""
                now_in_tz = datetime.datetime.now().astimezone(timezone)
                if comment:
                    comment_str = "%s; t_comment_added: %s" % (comment, now_in_tz)

                for alert in alerts:
                    if comment_str:
                        apiw.set_alert_comment(adom, alert['alertid'], comment_str)
                    apiw.set_alert_acknowledged(adom, alert['alertid'])

                apiw.logout()
                self.logger.debug("Connection to FortiManager was closed!")
                #
                return(True, "{} alerts has been acknowledged!".format(len(alerts)))
            else:
                return(False, 'Alert list is empty for {}'.format(user_id))

        #
        self.logger.critical("Failed to connect to FortiManager: code=\"{}\" msg=\"{}\" url=\"{}\"".format(
                                                                login_res[0]['status']['code'],
                                                                login_res[0]['status']['message'],
                                                                login_res[0]['url']))
        return (False, "Log in failed, %s" % login_res)

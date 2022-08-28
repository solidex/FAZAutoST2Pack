import os   
import sys
import json
import time
import datetime

from st2common.runners.base_action import Action

from FAZAPIWrapper import *




class GetNewAlertsAction(Action):
    def run(self, adom, alert_handler_name, event_handler_period, max_alert_age, limit, euname):

        apiw = FAZAPIWrapper(logger=self.logger)
        self.logger.debug("Trying connect to FortiManager: {}:{}@{}".format(
                                                                self.config['username'], 
                                                                self.config['faz_ip'],
                                                                self.config['password'][:2] + 8 * "*",
                                                                ))

        login_res = apiw.login(self.config['faz_ip'], self.config['username'], self.config['password'])

        if login_res[0]['status']['code'] == 0:
            self.logger.info("Successfully connected to FortiManager!")
            
            # query for new events
            self.logger.debug("Trying retrieve events from alert_handler_name={}/{} event_handler_period={} max_alert_age={} limit={} euname={}".format(
                adom, alert_handler_name, event_handler_period, max_alert_age, limit, euname))

            alerts = apiw.get_new_alerts(adom, alert_handler_name, event_handler_period, max_alert_age, limit, euname)
            self.logger.info("Found {} events on FortiManager!".format(len(alerts['data'])))

            # close connection to FortiManager
            apiw.logout()
            self.logger.debug("Connection to FortiManager was closed!")
            #
            if alerts:
                for alert in alerts['data']:
                    # fix missing euname
                    if 'euname' not in alert:
                        alert['euname'] = 'N/A'
                    if not alert['euname']:
                        alert['euname'] = 'N/A'


                if len(alerts['data']):
                    self.logger.debug("Print alerts to cache & return:\n{}\n<< Trimmed {} alerts >>".format(
                                        json.dumps(alerts['data'][:1], indent=4, sort_keys=True),
                                        len(alerts['data']) - 1,
                                        ))
                self.action_service.set_value(name='cached_alerts', value=json.dumps(alerts['data']), local=False)
            else:
                self.logger.warning("FortiManager returned an empty object for alerts: {}".format(alerts))

            #
            return (True, alerts)
        #
        #
        self.logger.critical("Failed to connect to FortiManager: code=\"{}\" msg=\"{}\" url=\"{}\"".format(
                                                                login_res[0]['status']['code'],
                                                                login_res[0]['status']['message'],
                                                                login_res[0]['url']))
        return (False, "Log in failed, %s" % login_res)

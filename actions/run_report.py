import sys
import json
import time
import datetime, pytz

from st2common.runners.base_action import Action

from FAZAPIWrapper import *

timezone = pytz.timezone("Europe/Minsk")





class RunReport(Action):

    def run(self, adom, email_to_address, report_id, user_id, alerts, ack, comment):
        #
        # get list of alerts to run report about
        if not alerts:
            self.logger.debug("function arg alerts={}, querying st2-datastore for cached alerts".format(alerts))
            alerts = self.action_service.get_value('cached_alerts', local=False)
        try:
            alerts = json.loads(alerts)
        except: 
            self.logger.exception("Failed to extract alerts from JSON: {}".format(alerts))
            return(False, 'Alerts cannot be extracted for {}'.format(user_id))
        #
        self.logger.info("Found {} alerts to be reported".format(len(alerts)))
        #
        # connect to FMG
        apiw = FAZAPIWrapper()
        self.logger.debug("Trying connect to FortiManager: {}:{}@{}".format(
                                                                self.config['username'], 
                                                                self.config['faz_ip'],
                                                                self.config['password'][:2] + 8 * "*",
                                                                ))
        #
        login_res = apiw.login(self.config['faz_ip'], self.config['username'], self.config['password'])
        #
        # debug output format
        output_format = self.config['output_format'].split(',')
        self.logger.info("Set report output formats: {}".format(','.join(output_format)))
        #
        if login_res[0]['status']['code'] == 0:
            self.logger.info("Successfully connected to FortiManager!")
            if len(alerts) == 0:
                return(False, '`alerts` parameter is emply!')

            filtered_alerts = []
            for alert in alerts:
                if alert['euname'] == user_id:
                    filtered_alerts.append(alert)
            #
            self.logger.info("{} alerts have been removed from results due to filter user_id={}".format(
                                len(alerts) - len(filtered_alerts), user_id))
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
                    self.logger.exception("Failed to create output-profile {}/{}!".format(adom, output_profile_name))
                    return (False, "Update output profile error")
                if upd_out_prof_rslt['status']['code'] != 0:
                    self.logger.error("Failed to create output-profile {}/{}!".format(adom, output_profile_name))
                    return (False, "Update output profile non-zero code, %s" % upd_out_prof_rslt)
    
                #
                self.logger.info("Output-profile {}/{} was successfully created!".format(adom, output_profile_name))
                #
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
                self.logger.debug("Generating report {}/{}".format(adom, report_id))

                #
                report_name = "n/a"
                while True:

                    status = apiw.get_report_status(adom, tid)
                    if status:
                        if status['progress-percent'] == 100:
                            report_name = status['name']
                            break
                    time.sleep(3)

                self.logger.debug("Report was successfully generated {}/{} name={}".format(adom, report_id, report_name))
                #
                now_in_tz = datetime.datetime.now().astimezone(timezone)
                comment_str = "report_id: %s; report_name: %s; sent_to: %s; t_generated: %s" % (tid, report_name, email_to_address, now_in_tz)
                for alert in alerts:
                    if comment:
                        apiw.set_alert_comment(adom, alert['alertid'], comment_str)
                    if ack:
                        apiw.set_alert_acknowledged(adom, alert['alertid'])

                apiw.logout()
                self.logger.debug("Connection to FortiManager was closed!")

                return(True, comment_str)
            else:
                return(False, 'Alert list is empty for {}'.format(user_id))
        #
        self.logger.critical("Failed to connect to FortiManager: code=\"{}\" msg=\"{}\" url=\"{}\"".format(
                                                                login_res[0]['status']['code'],
                                                                login_res[0]['status']['message'],
                                                                login_res[0]['url']))
        return (False, "Log in failed, %s" % login_res)

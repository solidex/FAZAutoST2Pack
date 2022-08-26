import sys
import json
import time
import logging
import datetime
from pytimeparse.timeparse import timeparse

from faz_jsonapi import FortiAnalyzerJSON


class FAZAPIWrapper:

    api = None

    def __init__(self, logger=logging.getLogger()):
        self.api = FortiAnalyzerJSON()
        self.api.verbose('off')
        self.api.debug('off')
        self.logger = logger

    def login(self, ip, username, password):
        return self.api.login(ip,username,password)

    def logout(self):
        self.api.verbose('off')
        self.api.debug('off')
        self.api.logout()

    def get_new_alerts(self, adom, alert_handler_name, event_handler_period, max_alert_age, limit, euname):
        url = '/eventmgmt/adom/%s/alerts' % adom
        now = datetime.datetime.now()
        start_time = now - datetime.timedelta(seconds=timeparse(max_alert_age))
        end_time = now - datetime.timedelta(seconds=timeparse(event_handler_period))

        #
        self.logger.debug("Calculated timestamps for filtering: now={} start_time={} end_time={}".format(
                                                        now, start_time, end_time))

        filter = "ackflag='no' and triggername='%s'" % alert_handler_name
        if euname:
            filter = "%s euname='%s'" % (filter, euname)
        params = {
          "apiver": 3,
          "limit": limit,
          "offset": 0,
          "time-range": {
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),  # Consider it as the FortiAnalyzer's timezone if the timezone info is not specified.
            "end": end_time.strftime("%Y-%m-%dT%H:%M:%S"),      # Consider it as the FortiAnalyzer's timezone if the timezone info is not specified.
          },
          "filter": filter,
          "url": url
        }
        self.logger.debug("Generated params for FortiManager querying: \n{}".format(
                                                        json.dumps(params, indent=4, sort_keys=True),
                                                        ))
        return self.api.get(url, data=params)

    def create_output_profile(self, adom, name):
        url = '/report/adom/%s/config/output' % adom
        params = {
          "apiver": 3,
          "data": {
            "name": name
          },
          "url": url
        }
        return self.api.add(url, data=params)

    def update_output_profile(self, adom, output_profile_name, server_name, email_from_address, email_to_address, email_subject, output_format):
        url = '/report/adom/%s/config/output/%s' % (adom, output_profile_name)
        params = {
          "apiver": 3,
          "data": {
            "email": "enable",
            "output-format": output_format,
            "email-subject": email_subject,
            "email-recipients": {
                "address": email_to_address,
                "email-from": email_from_address,
                "email-server": server_name
            }
          },
          "url": url
        }
        return self.api.update(url, data=params)

    def config_report(self, adom, report_id, first_log_time, last_log_time, ip, username, output_profile_name):
        url = "/report/adom/%s/config/schedule/%s" % (adom, report_id)

        period_start = [
          first_log_time.strftime("%H:%M:%S"),
          first_log_time.strftime("%Y/%m/%d")
        ]

        period_end = [
          last_log_time.strftime("%H:%M:%S"),
          last_log_time.strftime("%Y/%m/%d")
        ]

        filter = []
        if ip:
            filter.append({
              "name": "srcip",
              "opcode": 0,
              "status": 1,
              "value": ip,
            })
        if username:
            filter.append({
              "name": "user",
              "opcode": 0,
              "status": 1,
              "value": username,
            })
        params = {
            "apiver": 3,
            "data": {
                  "filter": filter,
                  "output-profile": output_profile_name,
                  "period-end": period_end,
                  "period-start": period_start,
                  "time-period": 16,
            },
            "url": url
        }
        response = self.api.update(url, data=params)

    def run_report(self, adom, report_id):
        url = "/report/adom/%s/run" % adom
        params = {
          "apiver": 3,
          "schedule": report_id,
          "url": url
        }
        return self.api.add(url, data=params)


    def get_report_status(self, adom, tid):
        url = "/report/adom/%s/run/%s" % (adom, tid)
        params = {
            "apiver": 3,
            "url": url
        }
        return self.api.get(url, data=params)

    def set_alert_comment(self, adom, alertid, comment):
        url = '/eventmgmt/adom/%s/alerts/comment' % adom
        params = {
          "apiver": 3,
          "alertid": [
            alertid
          ],
          "comment": comment,
          "url": url
        }
        return self.api.update(url, data=params)

    def set_alert_acknowledged(self, adom, alertid):
        url = '/eventmgmt/adom/%s/alerts/ack' % adom
        params = {
          "apiver": 3,
          "alertid": [
            alertid
          ],
          "url": url
        }
        return self.api.update(url, data=params)

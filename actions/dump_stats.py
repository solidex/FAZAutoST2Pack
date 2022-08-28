import sys
import json
import time
import datetime, pytz

from FAZAPIWrapper import *

from st2common.runners.base_action import Action

from st2client.client import Client
from st2client.models import KeyValuePair

timezone = pytz.timezone("Europe/Minsk")

STATS_TTL = 600

class DumpStats(Action):
    """
    _stat_st2_success_last 
    _stat_st2_not_success_last
    _stat_alerter_errors_last
    _stat_alerter_warnings_last
    _stat_reports_generated_last
    _stat_st2_success_total
    _stat_st2_not_success_total
    _stat_alerter_errors_total
    _stat_alerter_warnings_total
    _stat_reports_generated_total

    """
    def run(self, stats_str):
        self.logger.debug("Function argument stats_str={}".format(stats_str))
        try:
            stats = json.loads(stats_str.replace('\'','"'))
        except:
            self.logger.exception("Failed to extract stats from JSON")
            return (False, {})
        self.logger.info("Extracted current execution stats: {}".format(json.dumps(stats, indent=4, sort_keys=True)))
        #
        # set last
        metrics_last = dict()
        metrics_last['st2_success'] = 0
        metrics_last['st2_not_success'] = 0
        metrics_last['alerter_errors'] = 0
        metrics_last['alerter_warnings'] = 0
        metrics_last['reports_generated'] = 0
        #
        # load total
        metrics_total = dict()
        for metric_name in metrics_last.keys():
            if self.action_service.get_value('_stat_%s_total' % metric_name, local=False):
                metrics_total[metric_name] = int(self.action_service.get_value(name='_stat_%s_total' % metric_name, local=False))
            else:
                metrics_total[metric_name] = 0
        #
        self.logger.info("metrics_total are loaded from st2-datastore: \n{}".format(json.dumps(metrics_total, indent=4, sort_keys=True)))
        #
        for stat_name in stats:
            if stat_name['status'] == 'succeeded':
                metrics_last['st2_success'] += 1
            else:
                metrics_last['st2_not_success'] += 1
            #
            exit_code = stat_name['result']['output']['result']
            #
            if exit_code.startswith('ERR_'):
                metrics_last['alerter_errors'] += 1
            if exit_code.startswith('WARN_'):
                metrics_last['alerter_warnings'] += 1
            if exit_code == 'REPORT_GENERATED':
                metrics_last['reports_generated'] += 1
        #
        #
        self.logger.info("metrics_last are updated from last execution: \n{}".format(json.dumps(metrics_last, indent=4, sort_keys=True)))
        #
        # update metrics_total
        for metric_name in metrics_last.keys():
            metrics_total[metric_name] += metrics_last[metric_name]
        self.logger.info("metrics_total are updated from last execution: \n{}".format(json.dumps(metrics_total, indent=4, sort_keys=True)))
        #
        try:
            for metric_name in metrics_last.keys():
                    self.action_service.set_value(name='_stat_%s_last' % metric_name, value=str(metrics_last[metric_name]), ttl=STATS_TTL, local=False)
                    self.action_service.set_value(name='_stat_%s_total' % metric_name, value=str(metrics_total[metric_name]), local=False)
        except:
            self.logger.exception("Failed to save metrics in st2-datastore!")
            return (False, "%s" % ({ 'last': metrics_last, 'total': metrics_total}))

        return (True, "%s" % ({ 'last': metrics_last, 'total': metrics_total}))

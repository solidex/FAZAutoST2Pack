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

STATS_TTL = 600

class DumpStats(Action):

    def run(self, stats_str):
        self.logger.debug(stats_str)

        stats = json.loads(stats_str.replace('\'','"'))
        client = Client(base_url='http://localhost')

        m = dict()

        m['st2_success'] = 0
        m['st2_not_success'] = 0
        m['alerter_errors'] = 0
        m['alerter_warnings'] = 0
        m['reports_generated'] = 0

        mt = dict()
        # load total
        for k in m.keys():
            if client.keys.get_by_name(name='_stat_%s_total' % k):
                mt[k] = int(client.keys.get_by_name(name='_stat_%s_total' % k).value)
            else:
                mt[k] = 0

        for s in stats:
            if s['status'] == 'succeeded':
                m['st2_success'] += 1
            else:
                m['st2_not_success'] += 1

            exit_code = s['result']['output']['result']
            if exit_code.startswith('ERR_'):
                m['alerter_errors'] += 1
            if exit_code.startswith('WARN_'):
                m['alerter_warnings'] += 1
            if exit_code == 'REPORT_GENERATED':
                m['reports_generated'] += 1

        # upd total
        for k in m.keys():
            mt[k] += m[k]

        client = Client(base_url='http://localhost')
        for k in m.keys():
            client.keys.update(KeyValuePair(name='_stat_%s_last' % k, value=str(m[k]), scope='system', ttl=STATS_TTL))
            client.keys.update(KeyValuePair(name='_stat_%s_total' % k, value=str(mt[k]), scope='system'))

        return(True, "%s" % ({ 'last': m, 'total': mt}))

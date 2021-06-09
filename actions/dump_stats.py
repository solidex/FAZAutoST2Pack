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

        try:
            self.logger.debug(stats_str)
            stats_arr = stats_str.split(',')
            client = Client(base_url='http://localhost')
            for s in stats_arr:
                k = s.split('=')[0]
                v = s.split("=")[1]
                client.keys.update(KeyValuePair(name='_stat_%s' % k, value=v, scope='system', ttl=STATS_TTL))

            return(True, "Dumped!")
        except Exception as e:
            return(False, "Error! %s" % e.message)

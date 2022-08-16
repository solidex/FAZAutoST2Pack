import sys
import json
import time
import logging

import clickhouse_driver.dbapi as dbapi

from st2client.client import Client
from st2client.models import KeyValuePair

DB_TTL = 600

__all__ = [
    "GetAdminDataById"
]



class GetAdminDataById():

    def __init__(self): 
        #
        # for testing purposes only
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.DEBUG)

    def run(self, user_id):

        # client = Client(base_url='http://localhost')
        # cached_admin_info_kv = client.keys.get_by_name(KeyValuePair(name=user_id, scope='user'))
        cached_admin_info_kv = None

        admin_info = {
            'admin_name': '',
            'admin_phone': '',
            'admin_mail': ''
        }

        if cached_admin_info_kv:
            admin_info = json.loads(cached_admin_info.value)
            self.logger.debug('admin_info returned from cache, %s' % admin_info)
        else:
            self.logger.debug('Trying to get admin_info from DB...')

            try:
                dbapi.connect(host='172.18.0.2', user='default', password='', port=9000, database='a1')
                self.logger.info('Successfully connected to database...')
            except Exception as e:
                self.logger.exception('Failed to connect to database...')

            # testing purposes
            if user_id == '3752961995xx':
                admin_info = {
                    'admin_name': 'Pavel',
                    'admin_phone': '1-800-CALL-ME-BABY',
                    'admin_mail': 'provnov@solidex.by'
                }
            if user_id == '3752961995xy':
                admin_info = {
                    'admin_name': 'Pavel',
                    'admin_phone': '1-800-CALL-ME-BABY',
                    'admin_mail': 'admin@solidex.by'
                }
            self.logger.debug('admin_info returned from DB, %s' % admin_info)

        # client.keys.update(KeyValuePair(name=user_id, value=json.dumps(admin_info), ttl=DB_TTL, scope='user'))

        return(True, admin_info)



if __name__ == "__main__":
    get_admin_data = GetAdminDataById()
    #
    result = get_admin_data.run(user_id="3752961995xx")
    # print(result)
    #
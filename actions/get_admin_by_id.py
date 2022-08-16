import sys
import json
import time
import logging

from st2client.client import Client
from st2client.models import KeyValuePair

DB_TTL = 600

class GetAdminDataById():

    def __init__(self): 
        #
        # for testing purposes only
        self.logger = logging.getLogger()


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
    print(result)
    #
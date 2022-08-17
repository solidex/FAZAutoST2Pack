import os
import sys
import json
import time
import logging

import oracledb as dbapi
from st2client.client import Client
from st2client.models import KeyValuePair
from st2common.runners.base_action import Action

from key_management_handler import CustomKeyManagementHandler


DB_TTL = 600



class GetAdminDataById(Action):

    def run(self, user_id):
        keys = CustomKeyManagementHandler(base_url='http://localhost') 
        #
        admin_info = {
            'admin_name': '',
            'admin_phone': '',
            'admin_mail': ''
        }
        #
        db_host = keys.get_by_name(name="database_ip", scope='system').value
        db_port = keys.get_by_name(name="database_port", scope='system').value
        db_username = keys.get_by_name(name="database_username", scope='system').value
        db_password = keys.get_by_name(name="database_password", scope='system', decrypt=True).value
        db_query = keys.get_by_name(name="database_query", scope='system').value.format(user_id)
        #
        self.logger.debug('Database access parameters: {} | {} | {}'.format(
                        db_host+":"+db_port, 
                        db_username+":"+db_password[:2]+"*********",
                        db_query))

        #
        cached_admin_info_kv = keys.get_by_name(name=user_id, scope='user')
        #
        if cached_admin_info_kv:
            admin_info = json.loads(cached_admin_info_kv.value)
            self.logger.debug('admin_info returned from cache, %s' % admin_info)
        else:
            self.logger.debug('Trying to get admin_info from DB...')
            db_connection = dbapi.connect(host=db_host, user=db_username, password=db_password, port=db_port)
            try:
                db_cursor = db_connection.cursor()
                db_cursor.execute(db_query)
                #
                data_rows = db_cursor.fetchall()
                self.logger.debug('Sent query to database, found {} entries for {}'.format(
                                                                        len(data_rows), user_id))
                if len(data_rows) != 1:
                    self.logger.warning('Unexpected number of entries ({}) are found for {}'.format(
                                                                        len(data_rows), user_id))
                #
                admin_info["admin_phone"] = data_rows[0][0]
                admin_info["admin_name"] = data_rows[0][1]
                admin_info["admin_mail"] = data_rows[0][2]
            except Exception as e:
                self.logger.exception('Failed to query to database...')
                #
            finally:
                db_connection.close()
                self.logger.debug('Closed connection to database')
            #
            self.logger.debug('admin_info returned from DB, %s' % admin_info)
        #
        keys.update(KeyValuePair(name=user_id, value=json.dumps(admin_info), ttl=DB_TTL, scope='user'))
        return(True, admin_info)



if __name__ == "__main__":
    print(GetAdminDataById().run(user_id="3752961995xy"))
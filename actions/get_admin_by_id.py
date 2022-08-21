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


def oracledb_thin_client(*args, logger, **kwargs):
    try:
        logger.debug('Connecting to OracleDB using thin client...')
        db_connection = dbapi.connect(*args, **kwargs)
        return db_connection.cursor()
    except: 
        logger.exception('Failed to connect to OracleDB using thin client!')
        return None




def oracledb_thick_client(*args, logger, **kwargs):
    try:
        logger.debug('Connecting to OracleDB using thick client...')
        dbapi.init_oracle_client()
        db_connection = dbapi.connect(*args, **kwargs)
        return db_connection.cursor()
    except:         
        logger.exception('Failed to connect to OracleDB using thick client!')
        return None


def connect_to_oracledb(*args, **kwargs):
    thick_client = False if os.environ.get("USE_THICK_CLIENT", "YES") == "NO" else True
    # thick client should be changed by environment var
    if thick_client:
        return oracledb_thick_client(*args, **kwargs)
    else:
        return oracledb_thin_client(*args, **kwargs)



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
        db_connect_str = keys.get_by_name(name="database_connect_str", scope='system').value
        db_username = keys.get_by_name(name="database_username", scope='system').value
        db_password = keys.get_by_name(name="database_password", scope='system', decrypt=True).value
        db_query = keys.get_by_name(name="database_query", scope='system').value.format(user_id)
        #
        self.logger.debug('database connection string: {}'.format(db_connect_str))
        self.logger.debug('database username/password: {}'.format(db_username+":"+db_password[:2]+"*********"))
        self.logger.debug('database SQL query to execute: {}'.format(db_query))
        #
        #
        #
        cached_admin_info_kv = keys.get_by_name(name=user_id, scope='user')
        #
        if cached_admin_info_kv:
            admin_info = json.loads(cached_admin_info_kv.value)
            self.logger.debug('admin_info returned from cache, %s' % admin_info)
        else:
            cursor = connect_to_oracledb(dsn=db_connect_str, user=db_username, password=db_password, logger=self.logger)
            if cursor is None:  # thin & thick clients seems to be non-working
                self.logger.error('Failed to connect to database!')
                return (False, admin_info)
            #
            self.logger.debug('Database connection & cursor were created!')
            self.logger.debug('Executing SQL query on database...')
            #



            # admin_info["admin_phone"] = data_rows[0][0]
            # admin_info["admin_name"] = data_rows[0][1]
            # admin_info["admin_mail"] = data_rows[0][2]

            #
            # self.logger.debug('admin_info returned from DB, %s' % admin_info)
        #
        keys.update(KeyValuePair(name=user_id, value=json.dumps(admin_info), ttl=DB_TTL, scope='user'))
        return (True, admin_info)



if __name__ == "__main__":
    print(GetAdminDataById().run(user_id="3752961995xy"))
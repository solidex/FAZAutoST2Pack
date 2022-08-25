import os
import sys
import json
import time
import logging

import oracledb as dbapi
from st2common.runners.base_action import Action



DB_TTL = 600


def oracledb_thin_client(*args, logger, **kwargs):
    try:
        logger.debug('Connecting to OracleDB using thin client')
        db_connection = dbapi.connect(*args, **kwargs)
        return db_connection.cursor()
    except: 
        logger.exception('Failed to connect to OracleDB using thin client!')
        return None


def oracledb_thick_client(*args, logger, **kwargs):
    try:
        logger.debug('Connecting to OracleDB using thick client')
        dbapi.init_oracle_client()
        db_connection = dbapi.connect(*args, **kwargs)
        return db_connection.cursor()
    except:         
        logger.exception('Failed to connect to OracleDB using thick client!')
        return None


def connect_to_oracledb(*args, use_oracle_thick_client, **kwargs):
    thick_client = False if os.environ.get("USE_THICK_CLIENT", "YES") == "NO" else True
    # thick client should be changed by environment var
    if thick_client:
        return oracledb_thick_client(*args, **kwargs)
    else:
        return oracledb_thin_client(*args, **kwargs)




class GetAdminDataById(Action):

    def run_test(self, user_id):
        admin_info = {
            'admin_name': 'is_testing',
            'admin_phone': user_id,
            'admin_mail': 'admin@solidex.by',
        }
        self.logger.debug('admin_info returned from function GetAdminDataById.run_test, %s' % admin_info)
        return admin_info

    def run(self, user_id, use_oracle_thick_client):
        # Check if we're working in testing environment
        if self.config.get("is_testing", False):
            self.logger.warning("activate testing environment for the reason is_testing={}".format(
                                                                self.config.get("is_testing", False)))
            return self.run_test(user_id=user_id)
        #
        admin_info = {
            'admin_name': '',
            'admin_phone': user_id,
            'admin_mail': '',
        }
        #
        cached_admin_info_kv = self.action_service.get_value(user_id)
        #
        if cached_admin_info_kv:
            admin_info = json.loads(cached_admin_info_kv)
            self.logger.info('admin_info returned from cache, %s' % admin_info)
        else:
            #
            # database access configuration
            db_connect_str = self.config.get("db_connect_str", "<>")
            db_username = self.config.get("db_username", "<>")
            db_password = self.config.get("db_password", "<>")
            db_query = self.config.get("db_query", "<>").format(user_id)
            self.logger.debug('database connection string: {}'.format(db_connect_str))
            self.logger.debug('database login/password: {}:{}'.format(db_username, db_password[:2] + 8 * "*"))
            self.logger.debug('database SQL query to execute: \n{}'.format(db_query))
            #
            # connect & retrieve cursor from OracleDB
            self.logger.info('Trying to connect to database...')
            cursor = connect_to_oracledb(
                                        dsn=db_connect_str, 
                                        user=db_username, 
                                        password=db_password, 
                                        use_oracle_thick_client=use_oracle_thick_client,
                                        logger=self.logger
                                        )
            if cursor is None:  # connection seems to be non-working
                self.logger.error('Failed to connect to database!')
                return (False, admin_info)
            self.logger.info('Database connection & cursor were created!')
            #
            # executing SQL query
            self.logger.info('Executing SQL query on database...')
            try:
                data = cursor.execute(db_query).fetchall()
                self.logger.info('SQL query is successfully executed: {} result(s)'.format(len(data)))
            except:
                data = []
                self.logger.exception('SQL query is failed')
            #
            # process SQL results
            if len(data) == 0:
                self.logger.warning('No results found for {}'.format(user_id))
                return (True, admin_info)
            if len(data) > 1:
                self.logger.warning('Too many results found for {}').format(len(data), user_id)
            self.logger.info('Extracting values from SQL results...')
            try:
                admin_info["admin_mail"] = data[0][0]
                self.logger.info('SQL results are successfully extracted')
            except:
                self.logger.critical('Failed to extract values from SQL results: {}'.format(data[0]))
            #
            self.logger.debug('admin_info returned from database, %s' % admin_info)
            self.logger.debug('admin_info has added to cache for user_id={} TTL={}'.format(user_id, DB_TTL))
            self.action_service.set_value(name=user_id, value=json.dumps(admin_info), ttl=DB_TTL)
        #
        return (True, admin_info)



if __name__ == "__main__":
    print(GetAdminDataById().run(user_id="3752961995xy"))
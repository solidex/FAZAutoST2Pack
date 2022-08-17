import os
import json
import logging

from st2client.client import Client
from st2client.models import KeyValuePair


class CustomKeyManagementHandler():

    test_data_samples = {
        "3752961995xx": json.dumps({
            'admin_name': 'Pavel',
            'admin_phone': '1-800-CALL-ME-BABY',
            'admin_mail': 'provnov@solidex.by'
        }),
        "3752961995xy": json.dumps({
            'admin_name': 'Matvey',
            'admin_phone': '1-800-CALL-ME-BABY',
            'admin_mail': 'admin@solidex.by'
        }),
        "database_ip": "172.18.0.2",
        "database_port": "9000",
        "database_username": "default",
        "database_password": "",
        "database_query": "SELECT MSISDN, OrgName, OrgEmail from a1.msisdns where MSISDN='{}'",
    }


    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger()
        self.is_st2_available = False if os.environ.get("IS_ST2_AVAILABLE", "YES") == "NO" else True
        # 
        if not self.is_st2_available:
            self.logger.critical("IS_ST2_AVAILABLE=NO (Testing environment is activated) [!]")
        #
        if self.is_st2_available:
            self.client = Client(*args, **kwargs)
        else: 
            self.client = None


    def get_by_name_from_test_data(self, name, **kwargs):
        result_data = CustomKeyManagementHandler.test_data_samples.get(name)
        if result_data is None:
            return None
        else:
            return KeyValuePair(name=name, value=result_data)


    def get_by_name(self, name, **kwargs):
        if self.is_st2_available:
            return self.client.keys.get_by_name(name, **kwargs)
        else:
            return self.get_by_name_from_test_data(name, **kwargs)


    def update(self, instance, **kwargs):
        if self.is_st2_available:
            return self.client.keys.update(instance, **kwargs)
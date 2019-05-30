from odoo import models, fields, api

import urllib3
import logging
import json
_logger = logging.getLogger(__name__)

class imis_connect(models.Model):
    _name = 'imis.connect'
    
    @api.model
    def authenticate(self, username, password, url):
        _logger.info("Inside authenticate")
        http = urllib3.PoolManager()
        data = {}
        
        headers = urllib3.util.make_headers(basic_auth="admin:haha")
#         headers = {
#             "basic_auth":"admin:haha",
#             "Content-Type":"application/json"
#             }
        req = http.request('GET', url, headers=headers)
        resp_status = req.status    
        response = req.data
        _logger.info("========================")
        _logger.info("response")
        _logger.info(response)
        
    @api.model_cr
    def init(self):
        self.authenticate("admin", "haha", "https://192.168.33.20/insurance-integration/auth")



imis_connect()

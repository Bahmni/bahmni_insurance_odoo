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
        
        headers = urllib3.util.make_headers(basic_auth="%s:%s"%(username, password))
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
        
    
    @api.multi
    def _check_eligibility(self, nhis_number):
        _logger.info("Inside check_eligibility")
        http = urllib3.PoolManager()
        data = {}
        url = "https://192.168.33.20/insurance-integration/request/eligibility/%s"%(nhis_number)
        headers = urllib3.util.make_headers(basic_auth="admin:haha")
        req = http.request('GET', url, headers=headers)
        _logger.info("========= Response===============")
        response = json.loads(req.data.decode('utf-8'))
        _logger.info(response)
       
        
    @api.model_cr
    def init(self):
        self.authenticate("admin", "haha", "https://192.168.33.20/insurance-integration/auth")



imis_connect()

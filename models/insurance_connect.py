from odoo import models, fields, api

import urllib3
import logging
import json
_logger = logging.getLogger(__name__)

class insurance_connect(models.TransientModel):
    _name = 'insurance.connect'
    
    @api.model
    def authenticate(self, username, password, url):
        _logger.info("Inside authenticate")
        http = urllib3.PoolManager()
        data = {}
        headers = urllib3.util.make_headers(basic_auth="%s:%s"%(username, password))
        req = http.request('GET', url, headers=headers)
        resp_status = req.status    
        response = req.data
        _logger.info(response)
        
    
    @api.multi
    def _check_eligibility(self, nhis_number):
        _logger.info("Inside check_eligibility")
        http = urllib3.PoolManager()
        data = {}
        url = "https://192.168.33.20/insurance-integration/request/eligibility/%s"%(nhis_number)
        headers = urllib3.util.make_headers(basic_auth="%s:%s"%('admin', 'haha'))
        req = http.request('GET', url, headers=headers)
        _logger.info("========= Response===============")
        if req.status == 200:
            response = json.loads(req.data.decode('utf-8'))
            _logger.info(response)
            
        
insurance_connect()

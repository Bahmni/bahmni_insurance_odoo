from odoo import models, fields, api
from odoo.exceptions import UserError

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
        try:
            insurance_connect_configurations = self.env['insurance.config.settings'].get_insurance_connect_configurations()
            _logger.info(insurance_connect_configurations)
            if insurance_connect_configurations is None:
                raise UserError("Insurance configurations not set")
            
            http = urllib3.PoolManager()
            data = {}
            url = insurance_connect_configurations['base_url'] + "/request/eligibility/%s"
            url = url%(nhis_number)
            headers = urllib3.util.make_headers(basic_auth="%s:%s"%(insurance_connect_configurations['username'], insurance_connect_configurations['password']))
            req = http.request('GET', url, headers=headers)
            _logger.info("========= Response===============")
            if req.status == 200:
                response = json.loads(req.data.decode('utf-8'))
                _logger.info(response)
        except Exception as err:
            _logger.info("\n Processing event threw error: %s", err)
            raise
        
            
        
insurance_connect()

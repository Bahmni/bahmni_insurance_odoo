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
        insurance_connect_configurations = self.env['insurance.config.settings'].get_insurance_connect_configurations()
        if insurance_connect_configurations is None:
            raise UserError("Insurance configurations not set")
        url = self.prepare_url("/request/authenticate", insurance_connect_configurations)
        url = url%(nhis_number)
        http = urllib3.PoolManager()
        req = http.request('GET', url, headers=self.get_header(insurance_connect_configurations))
        
        resp_status = req.status    
        response = req.data
        _logger.info(response)
    
    def get_insurance_configurations(self):
        insurance_connect_configurations = self.env['insurance.config.settings'].get_insurance_connect_configurations()
        if insurance_connect_configurations is None:
            raise UserError("Insurance configurations not set")
        return  insurance_connect_configurations
    
    @api.model
    def _submit_claims(self, claim_request):
        _logger.info("Inside _submit_claims")
        if claim_request is None:
            raise UserError("Nothing to Claim")
            
        try:
            insurance_configs = self.get_insurance_configurations()
            url = self.prepare_url("/submit/claim", insurance_configs)
            encoded_data = json.dumps(claim_request).encode('utf-8')
            http = urllib3.PoolManager()
            req = http.request('POST', url, headers=self.get_header(insurance_configs), body = encoded_data)
                
            _logger.info("========= Response===============")
            _logger.info(req)
            if req.status == 200:
                response = json.loads(req.data.decode('utf-8'))
                _logger.info(response)
                return reponse
            else:
                raise UserError("Submission Failed. Please Check insurance-connect service and retry again.")
        except Exception as err:
            _logger.info("\n Processing event threw error: %s", err)
            raise
    
    @api.multi
    def _check_eligibility(self, nhis_number):
        _logger.info("Inside check_eligibility")
        try:
            insurance_connect_configurations = self.env['insurance.config.settings'].get_insurance_connect_configurations()
            if insurance_connect_configurations is None:
                raise UserError("Insurance configurations not set")
            
            url = self.prepare_url("/get/eligibilityResponse/%s", insurance_connect_configurations)
            url = url%(nhis_number)
            http = urllib3.PoolManager()
            req = http.request('GET', url, headers=self.get_header(insurance_connect_configurations))
            
            _logger.info("========= Response===============")
            if req.status == 200:
                response = json.loads(req.data.decode('utf-8'))
                _logger.info(response)
                return response
            else:
                raise UserError("Some issues with insurance connect service. Please verify and retry again")
            
        except Exception as err:
            _logger.info("\n Processing event threw error: %s", err)
            raise
        
    
    def prepare_url(self, end_point, insurance_connect_configurations):
        return insurance_connect_configurations['base_url'] + end_point
        
    def get_header(self, insurance_connect_configurations):
        return urllib3.util.make_headers(basic_auth="%s:%s"%(insurance_connect_configurations['username'], insurance_connect_configurations['password']))
          
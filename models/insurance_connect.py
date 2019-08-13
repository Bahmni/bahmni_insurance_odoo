from odoo import models, fields, api
from odoo.exceptions import UserError

import urllib3
import logging
import json
_logger = logging.getLogger(__name__)

class insurance_connect(models.TransientModel):
    _name = 'insurance.connect'
    
    @api.model
    def authenticate(self):
        _logger.info("Inside authenticate")
#         insurance_connect_configurations = self.env['insurance.config.settings'].get_insurance_connect_configurations()
#         if insurance_connect_configurations is None:
#             raise UserError("Insurance configurations not set")
    
        #Mocking insurance connect configurations
        insurance_connect_configurations = {
            'username': username,
            'password': password,
            'url': url
        }
        url = self.prepare_url("/request/authenticate", insurance_connect_configurations)
        #url = url%(nhis_number)
        http = urllib3.PoolManager()

        req = http.request('GET', url, headers=self.get_header(insurance_connect_configurations))
        
        if req.status == 200:
            #Display dialogue box for successful
            ola = 1
        else:
            raise UserError("Connection failed.")
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
            encoded_data = json.dumps(claim_request)
            _logger.info(encoded_data)
            http = urllib3.PoolManager()
            custom_headers = {'Content-Type': 'application/json'}
            headers = self.get_header(insurance_configs)
            custom_headers.update(headers)
            req = http.request('POST', url, headers=custom_headers, body = encoded_data)
            _logger.info("========= Response===============")
            _logger.info(req)
            if req.status == 200:
                response = json.loads(req.data.decode('utf-8'))
                _logger.info(response)
                return response
            else:
                response = json.loads(req.data.decode('utf-8'))
                _logger.info(response)
                raise UserError("Submission Failed. Please Check insurance-connect service and retry again.")
        except Exception as err:
            _logger.error("\n Processing event threw error: %s", err)
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
            
            self.response_processor(req)
            
        except Exception as err:
            _logger.error("\n Processing event threw error: %s", err)
            raise
        
    @api.multi
    def _get_visit(self, visit_uuid):
        _logger.info("Inside _check_visit")
        try:
            insurance_connect_configurations = self.env['insurance.config.settings'].get_insurance_connect_configurations()
            if insurance_connect_configurations is None:
                raise UserError("Insurance configurations not set")
            
            url = self.prepare_url("/insurance-integration/visit/%s", insurance_connect_configurations)
            url = url%(visit_uuid)
            http = urllib3.PoolManager()
            req = http.request('GET', url, headers=self.get_header(insurance_connect_configurations))
            self.response_processor(req)
            
        except Exception as err:
            _logger.error("\n Processing event threw error: %s", err)
            raise
    
    @api.multi
    def _track_claim(self, claim_id):
        _logger.info("Inside _track_claim")
        try:
            insurance_connect_configurations = self.env['insurance.config.settings'].get_insurance_connect_configurations()
            if insurance_connect_configurations is None:
                raise UserError("Insurance configurations not set")
            
            url = self.prepare_url("get/claimresponse/%s", insurance_connect_configurations)
            url = url%(claim_id)
            http = urllib3.PoolManager()
            req = http.request('GET', url, headers=self.get_header(insurance_connect_configurations))
            self.response_processor(req)
                    
        except Exception as err:
            _logger.error("\n Processing event threw error: %s", err)
            raise
    
    def response_processor(self, response):
        _logger.info("========= Response===============")
        if req.status == 200:
            response = json.loads(req.data.decode('utf-8'))
            _logger.info(response)
            return response
        else:
            _logger.error("\n Failed Request to insurance connect: %s", req)
            raise UserError("%s, %s \n Failed Request to insurance connect"%(req.error, req.message))
            
    
    def prepare_url(self, end_point, insurance_connect_configurations):
        return insurance_connect_configurations['base_url'] + end_point
        
    def get_header(self, insurance_connect_configurations):
        return urllib3.util.make_headers(basic_auth="%s:%s"%(insurance_connect_configurations['username'], insurance_connect_configurations['password']))

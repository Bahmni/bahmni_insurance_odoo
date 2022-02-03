from odoo import models, fields, api
from odoo.exceptions import UserError

import urllib3
import logging
import json
_logger = logging.getLogger(__name__)

class insurance_connect(models.TransientModel):
    _name = 'insurance.connect'


    def _resubmit_claim_fhir(self, claim_fhir_request):
        _logger.info("Inside _resubmit_claim_fhir")
        try:
            insurance_connect_configurations = self.env[
                'insurance.config.settings'].get_insurance_connect_configurations()
            if insurance_connect_configurations is None:
                raise UserError("Insurance configurations not set")
            url = self.prepare_url("/resubmit/fhir", insurance_connect_configurations)
            http = urllib3.PoolManager()
            custom_headers = {'Content-Type': 'application/json'}
            headers = self.get_header(insurance_connect_configurations)
            custom_headers.update(headers)
            encoded_data = claim_fhir_request
            _logger.info(encoded_data)
            response = http.request('POST', url, headers=custom_headers, body=encoded_data)
            return self.response_processor(response)
        except Exception as err:
            _logger.error("\n Processing event threw error: %s", err)
            raise


    @api.model
    def authenticate(self, username, password, url):
        _logger.info("Inside authenticate")
        insurance_connect_configurations = {
            'username': username,
            'password': password,
            'base_url': url
        }
        url = self.prepare_url("/request/authenticate", insurance_connect_configurations)
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
            if req.status == 200:
                _logger.info(req.status)
                response = json.loads(req.data.decode('utf-8'))
                _logger.info(response)
                return response
            elif req.status == 503:
                _logger.error(req.data)
                raise UserError("Insurance connect service not available. Please contact system administrator")
            elif req.status == 401:
                _logger.error(req.data)
                raise UserError("Please check credentials for insurance connect service and retry again")
            else:
                # raise UserError(req.data.decode('utf-8'))
                response = json.loads(req.data.decode('utf-8'))
                _logger.info(json.dumps(response))
                if response["operationOutComeException"] is None:
                    error_msg = "Claim Submission Failed, Please contact your app admin"
                else:
                    error_msg = response["operationOutComeException"]
                # error = "Submission Failed" % str(response["operationOutComeException"])
                raise UserError(error_msg)
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
            url = self.prepare_url("/check/eligibility/%s", insurance_connect_configurations)
            url = url%(nhis_number)
            _logger.info(url)
            http = urllib3.PoolManager()
            custom_headers = {'Content-Type': 'application/json'}
            headers = self.get_header(insurance_connect_configurations)
            custom_headers.update(headers)
            #encoded_data = json.dumps(elig_params)
            #_logger.info(encoded_data)
            req = http.request('GET', url, headers=custom_headers)
            return self.response_processor(req)
            
        except Exception as err:
            _logger.error("\n Processing event threw error: %s", err)
            raise

    @api.multi
    def _get_diagnosis(self, ext_uuid):
        _logger.info("Inside _get_diagnosis")
        try:
            insurance_connect_configurations = self.env['insurance.config.settings'].get_insurance_connect_configurations()
            if insurance_connect_configurations is None:
                raise UserError("Insurance configurations not set")
            url = self.prepare_url("/diagnosis/%s", insurance_connect_configurations)
            url = url%(ext_uuid)
            _logger.info(url)
            http = urllib3.PoolManager()
            custom_headers = {'Content-Type': 'application/json'}
            headers = self.get_header(insurance_connect_configurations)
            custom_headers.update(headers)
            #encoded_data = json.dumps(elig_params)
            #_logger.info(encoded_data)
            req = http.request('GET', url, headers=custom_headers)
            return self.response_processor(req)
            
        except Exception as err:
            _logger.error("\n Processing event threw error: %s", err)
            raise

    @api.multi
    def _get_claim_fhir(self, claim_id):
        _logger.info("Inside _get_claim_fhir")
        _logger.info(claim_id)
        try:
            insurance_connect_configurations = self.env[
                'insurance.config.settings'].get_insurance_connect_configurations()
            if insurance_connect_configurations is None:
                raise UserError("Insurance configurations not set")

            url = self.prepare_url("/get/claimRequest/%s", insurance_connect_configurations)
            url = url % claim_id
            http = urllib3.PoolManager()
            response = http.request('GET', url, headers=self.get_header(insurance_connect_configurations))
            return response
            # return self.response_processor(req)

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
            
            url = self.prepare_url("/visit/%s", insurance_connect_configurations)
            url = url%(visit_uuid)
            http = urllib3.PoolManager()
            req = http.request('GET', url, headers=self.get_header(insurance_connect_configurations))
            # raise UserError(json.dumps(req))
            return self.response_processor(req)
            
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
            
            url = self.prepare_url("/get/claimresponse/%s", insurance_connect_configurations)
            url = url%(claim_id)
            http = urllib3.PoolManager()
            req = http.request('GET', url, headers=self.get_header(insurance_connect_configurations))
            return self.response_processor(req)
                    
        except Exception as err:
            _logger.error("\n Processing event threw error: %s", err)
            raise
    
    def response_processor(self, response):
        _logger.info("========= Response ===============")
        _logger.info(response.status)

        if response.status == 200:
            response = json.loads(response.data.decode('utf-8'))
            _logger.info(json.dumps(response))
            return response
        elif response.status == 503:
            _logger.error(response.data)
            raise UserError("Insurance connect service not available.Please contact system administrator")
        elif response.status == 401:
            _logger.error(response.data)
            raise UserError("Please check credentials for insurance connect service and retry again")
        else:
            _logger.error("\n Failed Request to insurance connect: %s", response.data)
            response = json.loads(response.data.decode('utf-8'))
            raise UserError("%s, %s \n Failed Request to insurance connect"%(response['error'], response['message']))

    
    def prepare_url(self, end_point, insurance_connect_configurations):
        return insurance_connect_configurations['base_url'] + end_point
        
    def get_header(self, insurance_connect_configurations):
        return urllib3.util.make_headers(basic_auth="%s:%s"%(insurance_connect_configurations['username'], insurance_connect_configurations['password']))

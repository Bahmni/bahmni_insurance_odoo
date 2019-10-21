# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api
from datetime import datetime
import logging
import json
from _ast import Param

_logger = logging.getLogger(__name__)


class insurance_fhir(models.TransientModel):
    _name = 'insurance.fhir'
    _description = "Insurance Fhir "

    claim_code = fields.Char(string="Claim Code",  readonly=1)
    claim_fhir_request = fields.Text(string='Claim FHIR Request')

    @api.multi
    def action_reprocess_claim(self):
        _logger.info(self.claim_fhir_request)
        claim_in_db = self.env['insurance.claim'].search([('claim_code', '=', self.claim_code)])
        response = self.env['insurance.connect']._resubmit_claim_fhir(self.claim_fhir_request)
        if response:
            self.env['insurance.claim'].update_claim_from_claim_response(claim_in_db, response)


    @api.multi
    def _retrieve_claim_fhir(self, claim_code):
        _logger.info("_retrieve_claim_fhir")
        response = self.env['insurance.connect']._get_claim_fhir(claim_code)
        if response:
            if response.status == 200:
                response = json.loads(response.data.decode('utf-8'))
                _logger.info(json.dumps(response))
                response_str = json.dumps(response, sort_keys=True, indent=2, separators=(',', ': '))
                claim_fhir_response = {
                    'claim_code': claim_code,
                    'claim_fhir_request': response_str
                }
                return claim_fhir_response
            else:
                _logger.error("\n No Claim FHIR request available : %s", response.status)
                raise UserError(" No Claim FHIR request available ")

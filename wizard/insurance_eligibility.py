# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api
from datetime import datetime
import logging
import json
from _ast import Param
_logger = logging.getLogger(__name__)


class insurance_eligibility (models.TransientModel):
    _name = 'insurance.eligibility'
    _description = "Insurance Eligibility"
    
    insuree_name = fields.Char(string="Insuree Name",readonly=1)
    valid_from = fields.Datetime(string="Valid From", readonly=1)
    valid_till = fields.Datetime(string="Valid Till", readonly=1)
    eligibility_balance = fields.Float(string="Available Balance", readonly=1)
    nhis_number = fields.Char(string="NHIS Number", readonly=1)
    status = fields.Char(string="Status", readonly=1)
    card_issued = fields.Char(string="Card Issued", readonly=1)
    
    @api.multi
    def get_insurance_eligibility(self, partner_id):
        _logger.info("Inside map response")
        nhis_number = self.env['res.partner']._get_nhis_number(partner_id.id)
        if nhis_number:
            response = self.env['insurance.connect']._check_eligibility(nhis_number)
            self.insuree_name = partner_id.name
            self.valid_from =  response['validityFrom']
            self.valid_till =  response['validityTo']
            self.eligibility_balance =  response['eligibilityBalance'][0]['benefitBalance']
            self.nhis_number = nhis_number
            self.status = response['status']
            self.card_issued = response['cardIssued']
        return self
    
    @api.multi
    def get_insurance_details(self, partner_id):
        _logger.info("Inside _get_insurance_details")
        _logger.info(partner_id.id)
        nhis_number = self.env['res.partner']._get_nhis_number(partner_id.id)
        elig_request_param = {
            'chfID': nhis_number
        }

        if nhis_number:
            response = self.env['insurance.connect']._check_eligibility(elig_request_param)
            elig_response = {
                  'insuree_name':partner_id.name,
                  'nhis_number': nhis_number,
                  'valid_from': response['validityFrom'],
                  'valid_till': response['validityTo'],
                  'status': response['status'],
                  'card_issued': response['cardIssued'],
                  'eligibility_balance': response['eligibilityBalance'][0]['benefitBalance']
                }
            _logger.info(elig_response)
            return elig_response
        else:
            raise UserError("No Insurance Id, Please update and retry !")
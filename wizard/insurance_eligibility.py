# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import logging
import json
_logger = logging.getLogger(__name__)


class insurance_eligibility (models.TransientModel):
    _name = 'insurance.eligibility'
    _description = "Insurance Eligibility"
    
    insuree_name = fields.Char(string="Insuree Name",readonly=1)
    valid_from = fields.Datetime(string="Valid From", readonly=1)
    valid_till = fields.Datetime(string="Valid Till", readonly=1)
    balance = fields.Float(string="Available Balance", readonly=1)
    nhis_number = fields.Char(string="NHIS Number", readonly=1)
    
    @api.multi
    def get_insurance_eligibility(self, partner_id):
        _logger.info("Inside map response")
        nhis_number = self.env['res.partner']._get_nhis_number(partner_id.id)
        if nhis_number:
            response = self.env['insurance.connect']._check_eligibility(nhis_number)
            self.insuree_name = partner_id.name
            self.valid_from = datetime.now()
            self.valid_till = datetime.now()
            self.balance = 12344
            self.nhis_number = nhis_number
        return self
    
    @api.multi
    def _get_insurance_details(self, partner_id):
        _logger.info("Inside _get_insurance_details")
        nhis_number = self.env['res.partner']._get_nhis_number(partner_id.id)
        if nhis_number:
            response = self.env['insurance.connect']._check_eligibility(nhis_number)
            params = {
                  'insuree_name':partner_id.name,
                  'nhis_number': nhis_number,
                  'balance': 12344,
                  'valid_from': datetime.now(),
                  'valid_till': datetime.now()
                }
            return params

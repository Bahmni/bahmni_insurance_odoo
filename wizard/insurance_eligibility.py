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
    valid_till = fields.Datetime(string="Valid Till", readonly=1)
    eligibility_balance = fields.Float(string="Available Balance")
    nhis_number = fields.Char(string="NHIS Number", readonly=1)
    category = fields.Char(string="Category", readonly=1)

    @api.multi
    def action_save(self, values):
        _logger.info(self.eligibility_balance)
        return super(insurance_eligibility, self).write(values)

    @api.multi
    def get_insurance_eligibility(self, partner_id):
        _logger.info("Inside map response")
        nhis_number = self.env['res.partner']._get_nhis_number(partner_id.id)
        if nhis_number:
            response = self.env['insurance.connect']._check_eligibility(nhis_number)
            self.insuree_name = partner_id.name
            self.nhis_number = nhis_number
            if response['eligibilityBalance']:
                self.category = response['eligibilityBalance'][0]['category']
                self.valid_till = response['eligibilityBalance'][0]['validDate']
                self.eligibility_balance =  response['eligibilityBalance'][0]['benefitBalance']
        return self

    @api.multi
    def get_insurance_details(self, partner_id):
        _logger.info("Inside _get_insurance_details")
        _logger.info(partner_id.id)
        nhis_number = self.env['res.partner']._get_nhis_number(partner_id.id)
        if nhis_number:
            response = self.env['insurance.connect']._check_eligibility(nhis_number)
            elig_response = {
                'insuree_name':partner_id.name,
                'nhis_number': nhis_number,
            }
            if response['eligibilityBalance']:
                elig_response['category'] = response['eligibilityBalance'][0]['category']
                elig_response['valid_till'] = response['eligibilityBalance'][0]['validDate']
                elig_response['eligibility_balance'] =  response['eligibilityBalance'][0]['benefitBalance']
            _logger.info(elig_response)
            return elig_response
        else:
            raise UserError("No Insurance Id, Please update and retry !")

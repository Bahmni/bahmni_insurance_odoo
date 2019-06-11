# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import json
_logger = logging.getLogger(__name__)


class InsurnceEligibility(models.TransientModel):
    _name = 'insurance.eligibility'
    _description = "Insurance Eligibility"
    
    
    
    
    @api.onchange('partner_id')
    def _get_insurance_details(self):
        _logger.info("Inside _get_insurance_details")
        nhis_number = self.env['res.partner']._get_nhis_number(self.partner_id.id)
        if nhis_number:
            response = self.env['imis.connect']._check_eligibility(res_partner)
            _logger.info("========================")
            _logger.info(response)
            self.insuree_name = 'Dipak thapa'
            self.nhis_number = '12321323'
            self.balance = 12334
            
            
    
    
    
    
    
    
    
    insuree_name = fields.String(string="From Date")
    valid_from = fields.Date(string="Valid From")
    valid_till = fields.Date(MONTHS, string="Valid Till")
    balance = fields.Monetary(string='Available Balance')
    nhis_number = fields.Char(string="NHIS Number")

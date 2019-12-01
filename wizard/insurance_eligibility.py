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
    nhis_number = fields.Char(string="NHIS Number", readonly=1)
    eligibility_line_item = fields.One2many('insurance.eligibility.line','eligibility_request_id' ,string="eligibility lines")



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
            elig_response = self.env['insurance.eligibility'].create(elig_response)
            if response['eligibilityBalance']:
                _logger.critical(response)
                for elig_reponse_line in response['eligibilityBalance']:
                    elig_response_line = {
                        'eligibility_balance' : elig_reponse_line['benefitBalance'],
                        'valid_till' : elig_reponse_line['validDate'],
                        'category' : elig_reponse_line['category'],
                        'eligibility_request_id': elig_response.id
                     }
                    elig_response_line_from_db = self.env['insurance.eligibility.line'].search([('eligibility_request_id', '=', elig_response.id)])
                    elig_response_line = self.env['insurance.eligibility.line'].create(elig_response_line)
                    self.env['insurance.eligibility'].update({'eligibility_line_item', elig_response_line_from_db + elig_response_line })


                _logger.critical(elig_response.eligibility_line_item)


            _logger.info(elig_response)
            _logger.critical("response send")
            return elig_response
        else:
            raise UserError("No Insurance Id, Please update and retry !")



    class insurance_eligibility_line (models.TransientModel):
        _name = 'insurance.eligibility.line'
        _description = "Insurance Eligibility line"


        eligibility_request_id = fields.Many2one('insurance.eligibility',string="Insurance Eligibility")
        eligibility_balance = fields.Float(store=True, string="Available Balance")
        valid_till = fields.Datetime(store=True,string="Valid Till")
        category = fields.Char(store=True,string="Category")

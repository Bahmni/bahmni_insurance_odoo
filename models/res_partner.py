# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def _retrieve_nhis_number(self):
        _logger.info("Inside _retrieve_nhis_number")
        for partner in self:
            self.nhis_number = self._get_nhis_number(partner.id)
    
    @api.multi
    def _get_nhis_number(self, partner_id):
        _logger.info("Inside get_nhis number. Partner_id = %s", partner_id)
        attributes = self.env['res.partner.attributes'].search([('partner_id' , '=', partner_id),('name', '=', 'NHIS Number')])
        if attributes:
            return attributes.value
    @api.multi
    def _retrieve_nhis_status(self):
        # _logger.info("Inside _retrieve_nhis_number")
        for partner in self:
            self.InsuranceActive = self._get_nhis_status(partner.id)
    
    
    @api.multi
    def _retrieve_claim_id(self):
        # _logger.info("Inside _retrieve_nhis_number")
        for partner in self:
            self.InsuranceActive = self._get_claim_id(partner.id)

    @api.multi
    def _get_claim_id(self, partner_id):
        # _logger.info("Inside get_nhis number. Partner_id = %s", partner_id)
        attributes = self.env['res.partner.attributes'].search([('partner_id' , '=', partner_id),('name', '=', 'Claim Id')])
        if attributes:
            return attributes.value 
    @api.multi
    def _get_nhis_status(self, partner_id):
        # _logger.info("Inside get_nhis number. Partner_id = %s", partner_id)
        attributes = self.env['res.partner.attributes'].search([('partner_id' , '=', partner_id),('name', '=', 'NHIS Member Active')])
        if attributes:
            return attributes.value 
    nhis_number = fields.Char(string='NHIS Number', compute='_retrieve_nhis_number')
    InsuranceActive = fields.Boolean('Insurance Status', compute='_retrieve_nhis_status')
    claimID =fields.Char('Current Claim ID', compute='_retrieve_claim_id')
    uuid = fields.Char(string = "UUID")
    
    

class ResPartnerAttributes(models.Model):
    _name = 'res.partner.attributes'
    
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, index=True, readonly=False)
    name = fields.Char(string='Name', size=128, required=True)
    value = fields.Char(string='Value', size=128, required=False)
    
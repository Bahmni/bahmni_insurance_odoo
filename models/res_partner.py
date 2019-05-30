# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    attribute_ids = fields.One2many('res.partner.attributes', 'partner_id', string='Attributes')
    
    

class ResPartnerAttributes(models.Model):
    _name = 'res.partner.attributes'
    
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, index=True, readonly=False)
    name = fields.Char(string='Name', size=128, required=True)
    value = fields.Char(string='Value', size=128, required=False)
    

    

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class insurance_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'insurance.config.settings'

    username = fields.Char(string="Username", required=True, help="Username for insurance integration module")
    password = fields.Char(string="Password", required=True, help="Username for insurance integration module")
    base_url = fields.Char(string="Insurance Connect Service URL", required=True, help="Base URL for insurance integration module")
    claim_id_start_range = fields.Integer(string="Start Range", required=True, help="Start Value for claim code")
    claim_id_end_range = fields.Integer(string="Start Range", required=True, help="End Value for claim code")
    claim_number_next_val = fields.Integer(string="Next Value", required=True)
    
    @api.constrains("claim_id_start_range")
    def validate_start_range(self):
        if self.claim_id_start_range == None:
            raise ValidationError("The Start Range can\'t be empty")
        if self.claim_id_start_range > self.claim_id_end_range:
            raise ValidationError("The Start range can\'t be greater than End range")
        
         
    @api.constrains("claim_id_end_range")
    def validate_end_range(self):
        if self.claim_id_end_range == None:
            raise ValidationError("The Start Range can\'t be empty")
        if self.claim_id_end_range < self.claim_id_start_range:
            raise ValidationError("The End range can\'t be smaller than start range")
        
    @api.constrains("claim_number_next_val")
    def validate_next_val(self):
        if self.claim_number_next_val == None:
            raise ValidationError("The Next Values can\'t be empty")
        if self.claim_number_next_val < self.claim_id_start_range:
            raise ValidationError("The Next value range can\'t be smaller than start range")
        if self.claim_number_next_val > self.claim_id_end_range:
            raise ValidationError("The Next value range can\'t be greater than end range")
    
    
    @api.onchange('claim_id_start_range')
    def _change_next_val(self):
        self.claim_number_next_val = self.claim_id_start_range
    
    
    @api.model
    def _get_next_value(self):
        if self.claim_number_next_val:
            next_val = self.claim_number_previous_value + 1
        else:
            next_val = self.claim_id_start_range
        self.update({
            'claim_number_next_val': next_val
        })
        return next_val
    
    @api.model
    def get_insurance_connect_configurations(self):
        return {
            'username': self.env['ir.values'].get_default('insurance.config.settings', 'username'),
            'password': self.env['ir.values'].get_default('insurance.config.settings', 'password'),
            'base_url': self.env['ir.values'].get_default('insurance.config.settings', 'base_url')
        }
    
    @api.model
    def action_test_connection(self):
       response = self.env['insurance.connect'].authenticate()    
            
    @api.multi
    def set_params(self):
        self.ensure_one()
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'username', self.username)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'password', self.password)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'base_url', self.base_url)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_start_range', self.claim_id_start_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_end_range', self.claim_id_end_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_number_next_val', self.claim_number_next_val)
        
    
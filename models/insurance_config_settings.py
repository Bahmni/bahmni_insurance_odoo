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
    
    @api.one
    @api.constrains("claim_number_next_val")
    def validate_next_val(self):
        _logger.info("Inside validate_next_val")
        _logger.info("next value=%s",self.claim_number_next_val)
        if self.claim_number_next_val == None:
            raise ValidationError("The Next Values can\'t be empty")
        if self.claim_number_next_val < self.claim_id_start_range:
            raise ValidationError("The Next value range can\'t be smaller than start range")
        if self.claim_number_next_val > self.claim_id_end_range:
            raise ValidationError("The Next value range can\'t be greater than end range")
    
    
    @api.onchange('claim_id_start_range')
    def _change_next_val(self):
        self.claim_number_next_val = self.claim_id_start_range
    
    
    @api.one
    def _get_next_value(self):
        _logger.info("Inside validate_next_val")
        self.username = self.env['ir.values'].get_default('insurance.config.settings', 'username')
        self.password = self.env['ir.values'].get_default('insurance.config.settings', 'password')
        self.next_val = self.env['ir.values'].get_default('insurance.config.settings', 'claim_number_next_val')
        self.start_range = self.env['ir.values'].get_default('insurance.config.settings', 'claim_id_start_range')
        self.end_range = self.env['ir.values'].get_default('insurance.config.settings', 'claim_id_end_range')
        self.validate_next_val()
        claim_setting_configs = {
            'username': self.username,
            'password': self.password,
            'base_url': self.base_url,
            'claim_id_start_range': self.start_range,
            'claim_id_end_range': self.end_range,
            'claim_number_next_val': self.next_val + 1
        }
        _logger.info(claim_setting_configs)
        claim_in_db = self.env['insurance.config.settings'].create(claim_setting_configs)
        _logger.info(self.next_val)
        return self.next_val
    
    @api.model
    def get_insurance_connect_configurations(self):
        return {
            'username': self.env['ir.values'].get_default('insurance.config.settings', 'username'),
            'password': self.env['ir.values'].get_default('insurance.config.settings', 'password'),
            'base_url': self.env['ir.values'].get_default('insurance.config.settings', 'base_url')
        }
    
    @api.multi
    def action_test_connection(self):
        _logger.info("model username->%s", self.username)
        _logger.info("model password->%s",self.password)
        _logger.info("model url->%s",self.base_url)
        
        response = self.env['insurance.connect'].authenticate(self.username, self.password, self.base_url)
           
            
    @api.multi
    def set_params(self):
        self.ensure_one()
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'username', self.username)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'password', self.password)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'base_url', self.base_url)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_start_range', self.claim_id_start_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_end_range', self.claim_id_end_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_number_next_val', self.claim_number_next_val)
        
    
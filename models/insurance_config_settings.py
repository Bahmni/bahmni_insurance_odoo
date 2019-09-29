from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class insurance_config_settings(models.Model):
    _inherit = 'res.config.settings'
    _name = 'insurance.config.settings'

    username = fields.Char(string="Username", required=True, help="Username for insurance integration module")
    password = fields.Char(string="Password", required=True, help="Username for insurance integration module")
    base_url = fields.Char(string="Insurance Connect Service URL", required=True, help="Base URL for insurance integration module")
    claim_id_start_range = fields.Integer(string="Start Range", help="Start Value for claim code")
    claim_id_end_range = fields.Integer(string="Start Range", help="End Value for claim code")
    claim_number_next_val = fields.Integer(string="Next Value", readonly=True)
    insurance_journal = fields.Char(string="Insurance Journal", required=True, help="Name of the journal which will handle insurance payments")
    
    @api.constrains("claim_id_start_range")
    def validate_start_range(self):
        if not self.claim_id_start_range and not self.claim_id_end_range:
            return
        if not self.claim_id_start_range:
            raise ValidationError("The Start Range can\'t be empty")
        if self.claim_id_start_range > self.claim_id_end_range:
            raise ValidationError("The Start range can\'t be greater than End range")
        
         
    @api.constrains("claim_id_end_range")
    def validate_end_range(self):
        if not self.claim_id_start_range and not self.claim_id_end_range:
            return
        if not self.claim_id_end_range:
            raise ValidationError("The End Range can\'t be empty")
        if self.claim_id_end_range < self.claim_id_start_range:
            raise ValidationError("The End range can\'t be smaller than start range")
        
    @api.constrains("insurance_journal")
    def validate_insurance_journal(self):
        _logger.info("Inside validate_insurance_journal")
        _logger.info("insurance_journal = %s", self.insurance_journal)
        journal_name = self.env['account.journal'].search([('name', 'ilike', self.insurance_journal)])
        if not journal_name:
            raise ValidationError("Please add a valid journal")
    
    @api.one
    @api.constrains("claim_number_next_val")
    def validate_next_val(self):
        _logger.info("Inside validate_next_val")
        _logger.info("next value=%s",self.claim_number_next_val)
        if not self.claim_id_start_range and not self.claim_id_end_range:
            return
        if self.claim_number_next_val == None:
            raise ValidationError("The Next Values can\'t be empty")
        if self.claim_number_next_val < self.claim_id_start_range:
            raise ValidationError("The Next value range can\'t be smaller than start range")
        if self.claim_number_next_val > self.claim_id_end_range:
            raise ValidationError("The Next value range can\'t be greater than end range")
    
    
#     @api.onchange('claim_id_start_range')
#     def _change_next_val(self):
#         _logger.info("Inside _change_next_val")
#         _logger.info("next value=%s",self.claim_number_next_val)
#         self.claim_number_next_val = self.claim_id_start_range
    
    
    @api.multi
    def _get_next_value(self):
        _logger.info("Inside validate_next_val")
        
        _logger.info(self.username)
        _logger.info(self.password)
        _logger.info(self.claim_number_next_val)
        
#         insurance_config_setting = self.env['insurance.config.settings'].search([('external_visit_uuid', '=', visit_uuid)], order='create_date desc', limit=1)
        username = self.env['ir.values'].get_default('insurance.config.settings', 'username')
        password = self.env['ir.values'].get_default('insurance.config.settings', 'password')
        base_url = self.env['ir.values'].get_default('insurance.config.settings', 'base_url')
        next_val = self.env['ir.values'].get_default('insurance.config.settings', 'claim_number_next_val')
        start_range = self.env['ir.values'].get_default('insurance.config.settings', 'claim_id_start_range')
        end_range = self.env['ir.values'].get_default('insurance.config.settings', 'claim_id_end_range')
        insurance_journal = self.env['ir.values'].get_default('insurance.config.settings', 'insurance_journal')
#         self.validate_next_val()
#         next_val = insurance_config_setting.claim_number_next_val
#         updated_next_val = insurance_config_setting.claim_number_next_val + 1
#         

        claim_setting_configs = {
            'username': username,
            'password': password,
            'base_url': base_url,
            'claim_id_start_range': start_range,
            'claim_id_end_range': end_range,
            'claim_number_next_val': next_val + 1,
            'insurance_journal': insurance_journal
        }
#         _logger.info(claim_setting_configs)
#         insurance_config_setting.update({
#             'claim_number_next_val': updated_next_val
#         })
        configs = self.env['insurance.config.settings'].create(claim_setting_configs)
        self.update_params(configs)
        _logger.info(configs)
        return next_val
    
    @api.model
    def get_insurance_connect_configurations(self):
        return {
            'username': self.env['ir.values'].get_default('insurance.config.settings', 'username'),
            'password': self.env['ir.values'].get_default('insurance.config.settings', 'password'),
            'base_url': self.env['ir.values'].get_default('insurance.config.settings', 'base_url')
        }
        
    @api.model
    def get_insurance_journal(self):
        return self.env['ir.values'].get_default('insurance.config.settings', 'insurance_journal')
    
    @api.multi
    def action_test_connection(self):
        _logger.info("model username->%s", self.username)
        _logger.info("model password->%s",self.password)
        _logger.info("model url->%s",self.base_url)

        response = self.env['insurance.connect'].authenticate(self.username, self.password, self.base_url)
    
    @api.one
    def update_params(self, configs):
        _logger.info("Inside update_params")
        _logger.info("configs = %s", configs)
        self.ensure_one()
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'username', configs.username)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'password', configs.password)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'base_url', configs.base_url)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_start_range', configs.claim_id_start_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_end_range', configs.claim_id_end_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_number_next_val', configs.claim_number_next_val)      
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'insurance_journal', configs.insurance_journal)      
            
    @api.multi
    def set_params(self):
        _logger.info("Inside set_params")
        self.ensure_one()
        _logger.info(self.username)
        _logger.info(self.password)
        _logger.info(self.claim_number_next_val)
        
        
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'username', self.username)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'password', self.password)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'base_url', self.base_url)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_start_range', self.claim_id_start_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_end_range', self.claim_id_end_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_number_next_val', self.claim_number_next_val)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'insurance_journal', self.insurance_journal)
    
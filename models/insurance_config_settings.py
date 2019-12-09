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
    manually_setup_claim_code = fields.Boolean(string="Use default claim code", required=True, help="Use default claim code, or set it up manually")
    claim_id_start_range = fields.Integer(string="Start Range", help="Start Value for claim code")
    claim_id_end_range = fields.Integer(string="Start Range", help="End Value for claim code")
    claim_number_next_val = fields.Integer(string="Next Value")
    insurance_journal = fields.Char(string="Insurance Journal", required=True, help="Name of the journal which will handle insurance payments")
    add_visit_specific_product = fields.Boolean(string="Automatically add visit specific product", required=True, help="Add hospital visit, er visit, ipd visit claim lines automatically")
    
    @api.constrains("claim_id_start_range")
    def validate_start_range(self):
        
        '''
            Skip Start Range validation if its not manual setup for claim code
        '''
        if not self.manually_setup_claim_code:
            return
        
        if self.claim_id_start_range <= 0:
            raise ValidationError("The Start Range can\'t be less than or equal to 0")
        
        if not self.claim_id_start_range:
            raise ValidationError("The Start Range can\'t be empty")
        
        if self.claim_id_start_range > self.claim_id_end_range:
            raise ValidationError("The Start range can\'t be greater than End range")
         
    @api.constrains("claim_id_end_range")
    def validate_end_range(self):
        
        '''
            Skip End Range validation if its not manual setup for claim code
        '''
        if not self.manually_setup_claim_code:
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
        _logger.info("next value=%s", self.claim_number_next_val)
        
        '''
            Skip Next Value validation if its not manual setup for claim code
        '''
        if not self.manually_setup_claim_code:
            return
        if not self.claim_number_next_val:
            raise ValidationError("The Next Value can\'t be empty")
        if self.claim_number_next_val < self.claim_id_start_range:
            raise ValidationError("The Next value range can\'t be smaller than start range")
        if self.claim_number_next_val > self.claim_id_end_range:
            raise ValidationError("The Next value range can\'t be greater than end range")
    
    @api.multi
    def _get_claim_code_setup_option(self):
        _logger.info("Inside _get_claim_code_setup_option")
        manually_setup_claim_code = self.env['ir.values'].get_default('insurance.config.settings', 'manually_setup_claim_code')
        _logger.info("manually_setup_claim_code=%s", manually_setup_claim_code)
        return manually_setup_claim_code
    
    @api.multi
    def _get_visit_specific_claim_settings(self):
        _logger.info("Inside _get_visit_specific_claim_settings")
        add_visit_specific_product = self.env['ir.values'].get_default('insurance.config.settings', 'add_visit_specific_product')
        
        _logger.info("add_visit_specific_product=%s", add_visit_specific_product)
        return add_visit_specific_product
    
    @api.multi
    def _get_next_value(self):
        _logger.info("Inside _get_next_value")
        
        next_val = self.env['ir.values'].get_default('insurance.config.settings', 'claim_number_next_val')
        _logger.info("next_val = %s", next_val)
        
        # Increase next value by 1
        next_val = next_val + 1
        
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_number_next_val', next_val)      
        
        _logger.info("After Update, next_val = %s", next_val)
        
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
        _logger.info("model password->%s", self.password)
        _logger.info("model url->%s", self.base_url)

        response = self.env['insurance.connect'].authenticate(self.username, self.password, self.base_url)
        
    @api.multi
    def set_params(self):
        _logger.info("Inside set_params")
        self.ensure_one()
        
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'username', self.username)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'password', self.password)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'base_url', self.base_url)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'manually_setup_claim_code', self.manually_setup_claim_code)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_start_range', self.claim_id_start_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_end_range', self.claim_id_end_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_number_next_val', self.claim_number_next_val)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'insurance_journal', self.insurance_journal)
    

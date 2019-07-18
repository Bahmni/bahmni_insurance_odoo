from odoo import models, fields, api

class insurance_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'insurance.config.settings'

    username = fields.Char(string="Username", required=True)
    password = fields.Char(string="Password", required=True)
    base_url = fields.Char(string="Insurance Connect Service URL", required=True)
    claim_id_start_range = fields.Integer(string="Start Range")
    claim_id_end_range = fields.Integer(string="Start Range")
    claim_number_previous_value = fields.Integer(string="Previous number", readonly=True, required=True)
    
    @api.multi
    def default_get(self):
        res = super(insurance_config_settings, self).get_values()
        res.update(
            username=self.env['ir.values'].sudo().get_param('insurance.config.settings.username'),
            password=self.env['ir.values'].sudo().get_param('insurance.config.settings.password'),
            base_url=self.env['ir.values'].sudo().get_param('insurance.config.settings.base_url'),
            claim_id_start_range=self.env['ir.values'].sudo().get_param('insurance.config.settings.claim_id_start_range'),
            claim_id_end_range=self.env['ir.values'].sudo().get_param('insurance.config.settings.claim_id_end_range'),
            claim_number_previous_value=self.env['ir.values'].sudo().get_param('insurance.config.settings.claim_number_previous_value')
        )
        return res
      
    @api.multi
    def set_params(self):
        self.ensure_one()
        super(insurance_config_settings, self).set_values()
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'username', self.username)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'password', self.password)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'base_url', self.base_url)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_start_range', self.claim_id_start_range)
        self.env['ir.values'].sudo().set_default('insurance.config.settings', 'claim_id_end_range', self.claim_id_end_range)

    
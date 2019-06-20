from odoo import models, fields, api

class insurance_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'insurance.config.settings'

    username = fields.Char(string="Username", required=True)
    password = fields.Char(string="Password", required=True)
    base_url = fields.Char(string="Insurance Connect Service URL", required=True)
    claim_id_start_range = fields.Integer(string="Start Range")
    claim_id_end_range = fields.Integer(string="Start Range")
    
#     @api.model
#     def get_values(self):
#         res = super(insurance_config_settings, self).get_values()
#         res.update(
#             username=self.env['ir.config_parameter'].sudo().get_param('insurance.config.username'),
#             password=self.env['ir.config_parameter'].sudo().get_param('insurance.config.password'),
#             base_url=self.env['ir.config_parameter'].sudo().get_param('insurance.config.base_url'),
#             claim_id_start_range=self.env['ir.config_parameter'].sudo().get_param('insurance.config.claim_id_start_range'),
#             claim_id_end_range=self.env['ir.config_parameter'].sudo().get_param('insurance.config.claim_id_end_range')
#         )
#         return res
#      
#     @api.model
#     def set_values(self):
#         super(insurance_config_settings, self).set_values()
#         self.env['ir.config_parameter'].sudo().set_param('insurance.config.username', self.username)
#         self.env['ir.config_parameter'].sudo().set_param('insurance.config.password', self.password)
#         self.env['ir.config_parameter'].sudo().set_param('insurance.config.base_url', self.base_url)
#         self.env['ir.config_parameter'].sudo().set_param('insurance.config.claim_id_start_range', self.claim_id_start_range)
#         self.env['ir.config_parameter'].sudo().set_param('insurance.config.claim_id_end_range', self.claim_id_end_range)

    
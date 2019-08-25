from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    hospital_type = fields.Selection([
        ('PHC', 'PHC'),
        ('Hospital', 'Hospital')
        ],  string='Hospital Type', required=True, default="Hospital")
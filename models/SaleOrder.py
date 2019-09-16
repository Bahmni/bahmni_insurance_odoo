from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH'), ('partial', 'PARTIAL')], default='cash', string="Payment Type", required=True)

    


SaleOrder()
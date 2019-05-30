from odoo import models, fields, api

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    @api.one
    def _compute_amount(self):
        #self.claimable_amount = sum(if line.payment_type == 'insurance': round_curr(line.amount) for line in self.tax_line_ids)
        self.claimable_amount = 10

    claimable_amount = fields.Monetary(string="Claimable Amount", compute=_compute_amount)
    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH'), ('partial', 'PARTIAL')], default='cash', string="Payment Type", required=True)
    
    

sale_order()
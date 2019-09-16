from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH')], default='cash', string="Payment Type", required="True", help="Payment type accepted for this invoice", states={'draft': [('readonly', False)]})    
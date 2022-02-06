# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)
   

class PaymentJournalMapping (models.Model):
    _name = 'payment.journal.mapping'
    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH'), ('partial', 'Partial'), ('free', 'FREE')], default='cash', string="Payment Type", required="True")
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, change_default=True, index=True, track_visibility='always')
    
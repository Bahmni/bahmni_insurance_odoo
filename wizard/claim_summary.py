# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ClaimSummary(models.TransientModel):
    _name = 'claim.summary.wizard'
    _description = 'Insurance Claim Summary Report'

    date_start = fields.Datetime(required=True)
    date_end = fields.Datetime(required=True, default=fields.Datetime.now)

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start and self.date_end and self.date_end < self.date_start:
            self.date_end = self.date_start

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_end and self.date_end < self.date_start:
            self.date_start = self.date_end

    @api.multi
    def generate_report(self):
        _logger.info("Inside generate report")
        context = dict(self._context or {})
        context.update({'date_start': self.date_start, 'date_end': self.date_end})
        
        
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('insurance_claim_summary_report')
        
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': self.date_start, 'date_end': self.date_end,
            },
        }
        
        _logger.debug(data)
        
        return self.env['report'].get_action(self, 'bahmni_insurance_odoo.insurance_claim_summary', data=data)
    
    

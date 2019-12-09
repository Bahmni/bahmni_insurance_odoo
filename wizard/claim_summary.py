# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ClaimSummary(models.TransientModel):
    _name = 'claim.summary.wizard'
    _description = 'Insurance Claim Summary Report'

    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report(self):
        _logger.info("Inside generate report")
#         if (not self.env.user.company_id.logo):
#             raise UserError(_("You have to set a logo or a layout for your company."))
#         elif (not self.env.user.company_id.external_report_layout_id):
#             raise UserError(_("You have to set your reports's header and footer layout."))
#         data = {'date_start': self.start_date, 'date_end': self.end_date}
        context = dict(self._context or {})
        context.update({'date_start': self.start_date, 'date_end': self.end_date})
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'bahmni_insurance_odoo.insurance_claim_summary_report',
                'report_type': 'qweb-pdf',
                'data': context,
            }
#         return self.env.ref('bahmni_insurance_odoo.insurance_claim_summary_report').report_action([], data=data)



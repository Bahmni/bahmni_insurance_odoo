from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    @api.onchange('partner_id')
    def _get_nhis_number(self):
        _logger.info("Inside _get_nhis_number")
        partner_id = self.partner_id.id
        self.nhis_number = self.env['res.partner']._get_nhis_number(partner_id)
    
    @api.multi
    def check_eligibility(self):
        _logger.info("Inside check_eligibility")
        if self.nhis_number:
            partner_id = self.partner_id
            params = self.env['insurance.eligibility']._get_insurance_details(partner_id)
            ins_elg_obj = self.env['insurance.eligibility'].create(params)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Eligibility Check',
                'res_model': 'insurance.eligibility',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': ins_elg_obj.id,
                'view_id': self.env.ref('bahmni-insurance-odoo.insurance_eligibility_check_result_view', False).id,
                'target': 'new',
            }
        _logger.info("No NHIS number")
    
    @api.multi
    def print_consent(self):
        _logger.info("Inside print_consent")
        if self.nhis_number:
            context = dict(self._context or {})
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'bahmni-insurance-odoo.insurance_consent_form',
                'context': context,
            }

    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH'), ('partial', 'PARTIAL')], default='cash', string="Payment Type", required="True")
    nhis_number = fields.Char(string='NHIS Number', compute=_get_nhis_number)
    

class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH')], default='cash', string="Payment Type", required=True)

    
    
    
    
    
    
    
    
    
    
    
    
    

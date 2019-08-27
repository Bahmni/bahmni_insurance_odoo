from odoo import models, fields, api
from odoo.exceptions import UserError

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
    def action_invoice_create(self, grouped=False, final=False):
        _logger.info("Inside action_invoice_create overwritten")
        if self.check_if_insuree_is_eligible() == True:
            record = super(sale_order, self).action_invoice_create(grouped, final)
            for order in self:
                _logger.info("sale_order")
                _logger.info(order)
                self.env['insurance.claim']._create_claim(order)
            
    @api.multi
    def action_confirm(self):
        _logger.info("Inside action_confirm overwritten")
        if self.check_if_insuree_is_eligible() == True:
            super(sale_order, self).action_confirm()
    
    def check_if_insuree_is_eligible(self):
        _logger.info("Inside check_eligibility")
        # check if payment type is insurance/partial. If yes proceed with this flow else skip to default flow

        if self.payment_type in ('insurance', 'partial'):
            params = self.env['insurance.eligibility'].get_insurance_details(self.partner_id)
            claimable_amount = self.calculate_claimable_amount()
            # Check if insurance can be processed. Perform validations here. If true go ahead
            if claimable_amount <= params['eligibility_balance']:
                return True
            elif claimable_amount == 0.0 :
                raise UserError("Sales order can't be confirmed. No item present to be claimed.")
            else:
                raise UserError("Sales order can't be confirmed. No sufficient amount to process claim")

        return True
    
    @api.multi
    def calculate_claimable_amount(self):
        """
        Compute the total amounts that can be claimed
        """
        _logger.info("Inside calculate_claimable_amount")
        claimable_amount_total = 0.0
        for sale_order in self:
            for line in sale_order.order_line:
                if line.payment_type in ('insurance'):
                    imis_mapped_row = self.env['insurance.odoo.product.map'].search([('odoo_product_id', '=', line.product_id.id), ('is_active', '=', 'True')])
                    if imis_mapped_row is None or len(imis_mapped_row) == 0 :
                        _logger.debug("imis_mapped_row mapping not found")
                        raise UserError("%s is not mapped to insurance product"%(line.product_id.name))
                
                    if len(imis_mapped_row) > 1 :
                        _logger.debug("multiple mappings found")
                        raise UserError("Multiple mappings found for %s"%(line.product_id.name))
                        
                    claimable_amount_total += imis_mapped_row.insurance_price * line.product_uom_qty
        return claimable_amount_total
        
    @api.multi
    def check_eligibility(self):
        _logger.info("Inside check_eligibility")
        if self.nhis_number:
            partner_id = self.partner_id
            params = self.env['insurance.eligibility'].get_insurance_details(partner_id)
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
    external_id = fields.Char(string="External Id", help="This field is used to store encounter ID of bahmni api call")
    partner_uuid = fields.Char(string='Customer UUID', store=True, readonly=True)
    external_visit_uuid = fields.Char(string="External Id", help="This field is used to store visit ID of bahmni api call")

class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH')], default='cash', string="Payment Type", required=True)

    
    
    
    
    
    
    
    
    
    
    
    

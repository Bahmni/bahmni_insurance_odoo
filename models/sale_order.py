from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    @api.one
    def _compute_amount(self):
        claimable_amount = 0
        for sale_order in self:
            _logger.info("=========================")
            _logger.info(sale_order)
            if sale_order.payment_type != 'cash':
                insurance_sale_order_lines = self.env['sale.order.line'].search([('order_id' , '=', sale_order.id),('payment_type', '!=', 'cash')])
                for sale_order_line in insurance_sale_order_lines:
                    claimable_amount += sale_order_line.price_subtotal
        self.claimable_amount = claimable_amount
        
    @api.onchange('partner_id')
    def _get_nhis_number(self):
        _logger.info("Inside _get_nhis_number")
        partner_id = self.partner_id.id
        self.nhis_number = self.env['res.partner']._get_nhis_number(partner_id)
    
    @api.one
    def check_eligibility(self):
        _logger.info("Inside check_eligibility")
        _logger.info("\n\n\n\n===================")
        
        if self.nhis_number:
            _logger.info("")
            '''
            This function opens a window to display information of insuree
            '''
#             self.ensure_one()
#             ir_model_data = self.env['ir.model.data']
#             try:
#                 template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
#             except ValueError:
#                 template_id = False
#             try:
#                 compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
#             except ValueError:
#                 compose_form_id = False
#             ctx = dict()
#             ctx.update({
#                 'default_model': 'sale.order',
#                 'default_res_id': self.ids[0],
#                 'default_use_template': bool(template_id),
#                 'default_template_id': template_id,
#                 'default_composition_mode': 'comment',
#                 'mark_so_as_sent': True,
#                 'custom_layout': "sale.mail_template_data_notification_email_sale_order"
#             })
#             return {
#                 'type': 'ir.actions.act_window',
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_model': 'mail.compose.message',
#                 'views': [(compose_form_id, 'form')],
#                 'view_id': compose_form_id,
#                 'target': 'new',
#                 'context': ctx,
#             }
        
    @api.one
    def print_consent(self):
        _logger.info("\n\n\n\n===================")
        _logger.info("Inside print_consent")
        if self.nhis_number:
            return self.env['report'].get_action(self, 'insuree_consent_form')

    claimable_amount = fields.Monetary(string="Claimable Amount", compute=_compute_amount)
    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH'), ('partial', 'PARTIAL')], default='cash', string="Payment Type", required="True")
    nhis_number = fields.Char(string='NHIS Number', compute=_get_nhis_number)
    
    
    
    
    
    
    
    
    
    
    
    
    

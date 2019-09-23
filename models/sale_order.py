from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    @api.onchange('payment_type')
    def _change_payment_type(self):
        _logger.info("Inside _change_payment_type")
        
        for sale_order in self:
            for sale_order_line in sale_order.order_line:
                if sale_order.payment_type == 'cash' or sale_order.payment_type == 'insurance':
                    sale_order_line.update({
                        'payment_type': sale_order.payment_type
                        })
    @api.one          
    @api.onchange('partner_id')
    def _get_nhis_number(self):
        _logger.info("Inside _get_nhis_number")
        partner_id = self.partner_id.id
        self.nhis_number = self.env['res.partner']._get_nhis_number(partner_id)
    
    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        _logger.info("Inside action_invoice_create overwritten")
#         if self.check_if_insuree_is_eligible() == True:
#             record = super(sale_order, self).action_invoice_create(grouped, final)
            
        """
            Create the invoice associated to the SO.
            :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                            (partner_invoice_id, currency)
            :param final: if True, refunds will be generated if necessary
            :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}

        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    invoice_data = order._prepare_invoice()
                    for inv_data in invoice_data:
                        _logger.info("invoice_data=%s",inv_data)
                        invoice = inv_obj.create(inv_data)
                        references[invoice] = order
                        invoices[group_key] = invoice
                        invoices_origin[group_key] = [invoice.origin]
                        invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.client_order_ref)

                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
                                       'origin': ', '.join(invoices_origin[group_key])})

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            invoice.compute_taxes()
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        [inv.id for inv in invoices.values()]
            
        self.action_invoice_create_commons()
    
    @api.multi
    def action_invoice_create_commons(self):
        _logger.info("Inside action_invoice_create_commons overwritten")
        for order in self:
            _logger.info("sale_order")
            _logger.info(order)
            self.env['insurance.claim']._create_claim(order)
            
    @api.multi
    def action_confirm(self):
        _logger.info("Inside action_confirm overwritten")
        if self.check_if_insuree_is_eligible() == False:
            raise UserError("Insuree is not eligible. So sales order can't be confirmed")
        
        #Since its overwriting bahmni.sale_order class. Which is wrong behaviour. so copy pasting parent's code
        #TODO remove this
        #res = super(sale_order, self).action_confirm()
        
        res = False
        for order in self:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                order.force_quotation_send()
            order.order_line._action_procurement_create()
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
            res = True
        
        
        self.validate_delivery()
        #here we need to set condition for if the its enabled then can continue otherwise return True in else condition
        if self.env.user.has_group('bahmni_sale.group_skip_invoice_options'):
            _logger.info("Inside about to create invoice")
            
            #Getting id for insurance journal
            insurance_journal_name = self.env['insurance.config.settings'].get_insurance_journal()
            insurance_journal = self.env['account.journal'].search([('name', 'ilike', insurance_journal_name)])
            for order in self:
                created_invoices = []
                invoice_data = order._prepare_invoice()
                for inv_data in invoice_data:
                    _logger.info("invoice_data=%s",inv_data)
                    created_invoice = self.env['account.invoice'].create(inv_data)
                    _logger.info("created_invoice_state=%s",created_invoice.state)
                    for line in order.order_line:
                        '''
                            If current invoice is for insurance journal, then only add items with insurance payment
                            If current invoice is for cash(default) journal, then only add items with cash payment
                        '''
                        if ((created_invoice.journal_id.id != insurance_journal.id and line.payment_type.lower() == 'cash') or (created_invoice.journal_id.id == insurance_journal.id and line.payment_type.lower() == 'insurance')):
                            line.invoice_line_create(created_invoice.id, line.product_uom_qty)
    
                    # Use additional field helper function (for account extensions)
                    for line in created_invoice.invoice_line_ids:
                        line._set_additional_fields(created_invoice)
                    
                    
                    _logger.info("before compute taxes, created_invoice_state=%s",created_invoice.state)
                    
                    # Necessary to force computation of taxes. In account_invoice, they are triggered
                    # by onchanges, which are not triggered when doing a create.
                    created_invoice.compute_taxes()
                    created_invoice.message_post_with_view('mail.message_origin_link',
                        values={'self': created_invoice, 'origin': order},
                        subtype_id=self.env.ref('mail.mt_note').id)
                    
                    
                    _logger.info("after computing taxes, before invoice open, created_invoice_state=%s",created_invoice.state)
                    created_invoice.action_invoice_open()#Validate Invoice
                    
                    _logger.info("before append and after open, created_invoice_state=%s",created_invoice.state)
                    
                    created_invoices.append(created_invoice)
                    
                    _logger.info("After append created_invoice_state=%s",created_invoice.state)
                    
                #If eligible for claim then, proceed to create claim
                if self.check_if_insuree_is_eligible() == True:
                    self.action_invoice_create_commons()
                
                
                #Commenting Register payment as its causing issue in case of partial payment where 2 invoices are generated
                
                #Open payment dialouge box for ech invoice    
#                 reg_pay_form = self.env.ref('account.view_account_payment_invoice_form')
#                 
#                 for invoice in created_invoices :
#                     ctx = dict(
#                         default_invoice_ids = [(4, invoice.id, None)]
#                     )
#                     return {
#                         'name': _('Register Payment'),
#                         'type': 'ir.actions.act_window',
#                         'view_type': 'form',
#                         'view_mode': 'form',
#                         'res_model': 'account.payment',
#                         'views': [(reg_pay_form.id, 'form')],
#                         'view_id': reg_pay_form.id,
#                         'target': 'new',
#                         'context': ctx,
#                     }
                
        else:
            return res
        
        
    def check_if_insuree_is_eligible(self):
        _logger.info("Inside check_if_insuree_is_eligible")
        
        self.check_eligibility();
        
        #TODO remove this 
        return True
    
        # check if payment type is insurance/partial. If yes proceed with this flow else skip to default flow
        if self.payment_type in ('insurance', 'partial'):
            params = self.env['insurance.eligibility'].get_insurance_details(self.partner_id)
            claimable_amount = self.calculate_claimable_amount()
            
            #Check if insurance can be processed. Perform validations here. If true go ahead
            if params and claimable_amount <= params['eligibility_balance']:
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
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        _logger.info("Inside _prepare_invoice")
        self.ensure_one()
        
        '''
            Check payment type
            If payment type is cash then default journal i.e. cash
            If payment type is insurance then use insurance journal
        '''
        invoice_vals = []
        if self.payment_type == 'insurance':
            _logger.info("Inside Insurance payment processing")
            
            #Get Insurance journal
            insurance_journal = self.env['insurance.config.settings'].get_insurance_journal()
            
            journal = self.env['account.journal'].search([('name', 'ilike', insurance_journal)])
            
            if not journal:
                raise UserError(_('Please define a insurance journal for this company'))
            
            invoice_vals.append(self._prepare_invoice_commons(journal.id, 'insurance'))
        elif self.payment_type == 'cash':
            _logger.info("Inside cash payment processing")
            invoice_vals.append(self._prepare_invoice_for_cash_payment())
        elif self.payment_type == 'partial':
            _logger.info("Inside partial payment processing")
            
            #Get Insurance journal
            insurance_journal = self.env['insurance.config.settings'].get_insurance_journal()
            journal = self.env['account.journal'].search([('name', 'ilike', insurance_journal)])
            
            if not journal:
                raise UserError(_('Please define a insurance journal for this company'))
            
            #Invoice values for insurance payment
            invoice_vals.append(self._prepare_invoice_commons(journal.id, 'insurance'))
            
            #Invoice values for cash payment
            invoice_vals.append(self._prepare_invoice_for_cash_payment())
            
        else:
            raise UserError("Payment type not set") 
        return invoice_vals
    
    @api.multi
    def _prepare_invoice_for_cash_payment(self):   
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        payment_type = 'cash'
        return self._prepare_invoice_commons(journal_id, payment_type)
        
    @api.multi
    def _prepare_invoice_commons(self, journal_id, payment_type):    
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'discount_type': self.discount_type,
            'discount_percentage': self.discount_percentage,
            'disc_acc_id': self.disc_acc_id.id,
            'discount': self.discount,
            'payment_type': payment_type
        }
        return invoice_vals
      
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
        else:
            _logger.info("No NHIS number")
            raise UserError("No Insuree Id, Please update and retry !")
    
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

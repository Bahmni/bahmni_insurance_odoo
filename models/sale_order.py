from odoo import models, fields, api, _
from odoo.exceptions import UserError,Warning
from odoo.tools import float_is_zero
from datetime import datetime as dt
import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    @api.onchange('partner_id')
    def _get_nhis_number(self):
        _logger.info("Inside _get_nhis_number")
        for sale_order in self:
            partner_id = sale_order.partner_id.id
            if partner_id:
                sale_order.nhis_number = self.env['res.partner']._get_nhis_number(partner_id)
                if sale_order.nhis_number:
                    sale_order.payment_type == 'insurance'
                    sale_order.update({
                        'payment_type': 'insurance'
                        })
    
    @api.multi
    def _value_search(self, operator, value):
        recs = self.search([]).filtered(lambda x : x.shop_id ==  1 )
        if recs:
            return [('id', 'in', [x.id for x in recs])]
    
    @api.onchange('partner_id')
    def _get_claim_id(self):
        _logger.info("Inside _get_claim_id")
        for sale_order in self:
            partner_id = sale_order.partner_id.id
            if partner_id:
                sale_order.claim_id = self.env['res.partner']._get_claim_id(partner_id)
    @api.multi
    def get_current_user(self):
        for record in self:
            record.logged_user = record.env.uid
            record.logged_user_shop =record.env.user.shop_id.name
            isSame = False
            if record.env.user.shop_id.id == record.shop_id.id:
                isSame = True   
            record.isFromSameShop =isSame
            record.update({
                'logged_user': record.env.uid,
                'logged_user_shop': record.env.user.shop_id.name,
                'isFromSameShop': isSame
                })        
        # return {'value': {'logged_user': se.logged_user,'logged_user_shop':record.env.user.shop_id}}
        #   return {'value': {'payment_type': 'cash'}}
        # self.logged_user_shop = self.env.uid.shop_id
    
    @api.onchange('partner_id')
    def _get_nhis_status(self):
        _logger.info("Inside _get_nhis_status")
        for sale_order in self:
            partner_id = sale_order.partner_id.id
            if partner_id:
                sale_order.InsuranceActive = self.env['res.partner']._get_nhis_status(partner_id)
                
    
    def getInsuranceCost(self,productData):
        # resData = self.env('insurance.odoo.product.map').search(self._cr, self._uid, [( 'odoo_product_id', 'in', productData.id) ])
        resData =self.env['insurance.odoo.product.map'].search([('odoo_product_id', '=', productData.id)], limit=10)
        # raise UserError(_('getting insurance cost of '+ str(len(resData))))
        if len(resData) == 0:
            return -1222.5
            # raise UserError(_('Product not found in mapping. Please contact admin.'))
        else:
            return resData[0].insurance_price
    

    @api.onchange('payment_type')
    def _change_payment_type(self):
        # raise UserError(self.logged_user_shop)
        _logger.info("Inside _change_payment_type")
        hasError = False
        errorProducts = ""
        counter = 1
        for sale_order in self:
            for sale_order_line in sale_order.order_line:
                if sale_order.payment_type == 'cash' :
                    sale_order_line.update({
                        'payment_type': sale_order.payment_type,
                        'price_unit':sale_order_line.product_id.list_price

                        })
                if sale_order.payment_type == 'free' :
                    sale_order_line.update({
                        'payment_type': sale_order.payment_type,
                        'price_unit':0
                        })
                if sale_order.payment_type == 'insurance':
                    if self.nhis_number:
                        insurance_cost = self.getInsuranceCost(sale_order_line.product_id)
                        if insurance_cost == -1222.5:
                            hasError = True
                            if sale_order_line.product_id.name not in errorProducts: 
                                errorProducts = errorProducts+ "\n" + str(counter) + ". "+str(sale_order_line.product_id.name) 
                                counter=counter+1
                            sale_order_line.update({
                                'payment_type': sale_order.payment_type
                                })
                        else:
                            sale_order_line.update({
                                'payment_type': sale_order.payment_type,
                                'price_unit':insurance_cost
                                })
                    else:
                            return {'warning': {'title':'Warning Main!!!','message':'Payment type \'Insurance\' can be selected for patient with valid insuree id only.'},'value': {'payment_type': 'cash'}}
        if hasError == True:
             return {'warning': {'title':'Warning Main!!!','message':'All product in the list are not available for insurance claim. Please contact admin. \nProducts are :\n'+ str(errorProducts)}}
    
    @api.onchange("order_line")
    def on_change_state(self):
        cash =False
        insurance = False
        free = False
        for sale_order in self:
            for sale_order_line in sale_order.order_line:
                if sale_order_line.payment_type == 'cash':
                    cash =True
                if sale_order_line.payment_type == 'free':
                    free =True
                if sale_order_line.payment_type == 'insurance':
                    if self.nhis_number:
                        insurance =True
                        sale_order.update({'payment_type': 'partial'})
                    else:
                        return {'warning': {'title':'Warning!!!','message':'Payment type \'Insurance\' can be selected for patient with valid insuree id only.'},'value': {'payment_type': 'cash'}}
        if(cash and insurance and free):
            return {'value': {'payment_type': 'partial'}}
        elif(cash and free):
            return {'value': {'payment_type': 'partial'}}
        elif(cash and insurance):
            return {'value': {'payment_type': 'partial'}}
        elif(free and insurance):
            return {'value': {'payment_type': 'partial'}}
        elif(cash):
            return {'value': {'payment_type': 'cash'}}
        elif(free):
            return {'value': {'payment_type': 'free'}}
        elif(insurance):
            if self.nhis_number:
                return {'value': {'payment_type': 'insurance'}}
            else:
                 return {'warning': {'title':'Warning!!!','message':'Payment type \'Insurance\' can be selected for patient with valid insuree id only.'},'value': {'payment_type': 'cash'}}

    def setCashTypeLine(self):
        return {'warning': {'title':'Warning FOR INSURANCE!!!','message':'Payment typess \'Insurance\' can be selected for patient with valid insuree id only.'},'value': {'payment_type': 'cash'}}
    
    
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
                        
                        if line.qty_to_invoice > 0:
                            self.line_invoice_addition(line, invoice)
                        elif line.qty_to_invoice < 0 and final:
                            self.line_invoice_addition(line, invoice)
                        
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.client_order_ref)

                    if line.qty_to_invoice > 0:
                        self.line_invoice_addition(line, invoices[group_key])
                    elif line.qty_to_invoice < 0 and final:
                        self.line_invoice_addition(line, invoices[group_key])

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
                                       'origin': ', '.join(invoices_origin[group_key])})

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            _logger.info("Invoice line items, invoice_data=%s",invoice)
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
            
        self.action_invoice_create_commons(order)
    
    
    def line_invoice_addition(self, line, invoice):
        if line.qty_to_invoice > 0:
            line.invoice_line_create(invoice.id, line.qty_to_invoice)
        elif line.qty_to_invoice < 0 :
            line.invoice_line_create(invoice.id, line.qty_to_invoice)
    
    @api.multi
    def action_invoice_create_commons(self, order):
        _logger.info("Inside action_invoice_create_commons  overwritten")
        for order in self:
            _logger.info("sale_order")
            _logger.info(order)
            self.env['insurance.claim']._create_claim(order)
            
    @api.multi
    def action_confirm(self):
        _logger.info("Inside action_confirm overwritten")
        # if self.check_if_insuree_is_eligible() == False:
        #     raise UserError("Insuree is not eligible. So sales order can't be confirmed")
        
        #Since its overwriting bahmni.sale_order class. Which is wrong behaviour. so copy pasting parent's code
        #TODO remove this
        #res = super(sale_order, self).action_confirm()
        
        res = False
        crteam = self.env['crm.team'].search([])
        userTeam = None
        for data in crteam:
            for member in data.member_ids:
                if member == self.env.user:
                    userTeam = data
        for order in self:
            order.user_id=self.env.user
            order.team_id=userTeam
            order.update({
                                'user_id': self.env.user,
                                'team_id': userTeam
                                })
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
                    
                    created_invoices.append(self.create_invoice_line_commons(created_invoice, order, insurance_journal))
                    
                    
                #If eligible for claim then, proceed to create claim
                # if self.check_if_insuree_is_eligible() == True:
                self.action_invoice_create_commons(order)
                
                
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
    
    def create_invoice_line_commons(self, created_invoice, order, insurance_journal):
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
                
        return created_invoice
           
        
    def check_if_insuree_is_eligible(self):
        _logger.info("Inside check_if_insuree_is_eligible")
        
        # check if payment type is insurance/partial. If yes proceed with this flow else skip to default flow
        if self.payment_type in ('insurance', 'partial'):
            self.check_eligibility();
            
            # return True;
            #TODO Remove this comment section when eligibilty response is fixed
            params = self.env['insurance.eligibility'].get_insurance_details(self.partner_id)
            claimable_amount = self.calculate_claimable_amount()
            eligibleDate=params.eligibility_line_item.valid_till
            eligilbleUpto = dt.strptime(eligibleDate, "%Y-%m-%d %H:%M:%S")
            today=dt.today().strftime("%Y-%m-%d %H:%M:%S")
            todayDate = dt.strptime(today, "%Y-%m-%d %H:%M:%S")
            #Check if insurance can be processed. Perform validations here. If true go ahead
            if params and claimable_amount <= params.eligibility_line_item.eligibility_balance and eligilbleUpto > todayDate:
                return True
            elif eligilbleUpto < todayDate :
                raise UserError("Insurance has been expired. No item can be claimed.")
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
                        # raise UserError("%s is not mapped to insurance product"%(line.product_id.name))
                
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
            elig_response = self.env['insurance.eligibility'].get_insurance_details(partner_id)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Eligibility Check',
                'res_model': 'insurance.eligibility',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': elig_response.id,
                'view_id': self.env.ref('bahmni_insurance_odoo.insurance_eligibility_check_result_view', False).id,
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
                'report_name': 'bahmni_insurance_odoo.insurance_consent_form',
                'context': context,
            }
    
    InsuranceActive = fields.Boolean('Insurance Status', compute=_get_nhis_status)
    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH'), ('partial', 'PARTIAL'), ('free', 'FREE')], default='cash', string="Payment Type", required="True")
    nhis_number = fields.Char(string='NHIS Number', compute=_get_nhis_number)
    claim_id = fields.Char(string='NHIS Number', compute=_get_claim_id)
    external_id = fields.Char(string="External Id", help="This field is used to store encounter ID of bahmni api call")
    partner_uuid = fields.Char(string='Customer UUID', store=True, readonly=True)
    external_visit_uuid = fields.Char(string="External Id", help="This field is used to store visit ID of bahmni api call")
    care_setting = fields.Selection([('opd', 'OPD'), ('ipd', 'IPD'), ('free', 'OPD'),('proxy', 'OPD'), ('follow up', 'OPD'), ('emergency', 'ER')], default='opd',  string="Care Setting", required="True")
    logged_user= fields.Char(string='Current User',  store=False, compute=get_current_user)
    logged_user_shop= fields.Char(string='Current Users Shop',  store=False,compute=get_current_user)
    isFromSameShop = fields.Boolean('Same Shop',  store=False,compute=get_current_user)
class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH'), ('free', 'FREE')], default='cash', string="Payment Type", required=True)


    def getInsuranceCost(self,productData):
        # resData = self.env('insurance.odoo.product.map').search(self._cr, self._uid, [( 'odoo_product_id', 'in', productData.id) ])
        resData =self.env['insurance.odoo.product.map'].search([('odoo_product_id', '=', productData.id)], limit=10)
        # raise UserError(_('getting insurance cost of '+ str(len(resData))))
        if len(resData) == 0:
            return -1222.5
            # raise UserError(_('Product not found in mapping. Please contact admin.'))
            return {'warning': {'title':'Warning!!!','message':'Product not found in mapping. Please contact admin.'},'value': {'payment_type': 'cash'}}
        else:
            return resData[0].insurance_price
    
    @api.onchange('product_id')
    def _change_product_id(self):
        for sale_order_line in self:
            if self.order_id.nhis_number:
                insurance_cost = self.getInsuranceCost(sale_order_line.product_id)
                self.payment_type='insurance'
                if insurance_cost == -1222.5:
                    return {'warning': {'title':'Warning!!!','message':'Product not found in mapping. Please contact admin.'}}
                else:
                    return {'value': {'price_unit':insurance_cost,'payment_type': 'cash'}}

    @api.onchange('payment_type')
    def _change_payment_type(self):
        _logger.info("Inside _change_payment_type")
        for sale_order_line in self:
            if self.order_id.nhis_number:
                insurance_cost = self.getInsuranceCost(sale_order_line.product_id)
                if insurance_cost == -1222.5:
                    return {'warning': {'title':'Warning!!!','message':'Product not found in mapping. Please contact admin.'}}
                else:
                    return {'value': {'price_unit':insurance_cost}}
            if sale_order_line.payment_type == 'cash':
                return {'value': {'price_unit': sale_order_line.product_id.list_price}}
            if sale_order_line.payment_type == 'free' :
                return {'value': {'price_unit':0}}
            if sale_order_line.payment_type == 'insurance' :
                if self.order_id.nhis_number:
                    insurance_cost = self.getInsuranceCost(sale_order_line.product_id)
                    if insurance_cost == -1222.5:
                        return {'warning': {'title':'Warning!!!','message':'Product not found in mapping. Please contact admin.'}}
                    else:
                        return {'value': {'price_unit':insurance_cost}}
                else:
                    return {'warning': {'title':'Warning!!!','message':'Payment type \'Insurance\' can be selected for patient with valid insuree id only.'},'value': {'payment_type': 'cash'}}

    @api.onchange('lot_id')
    def on_change_lot(self):
        _logger.info("Inside order line _change_payment_type")
        for record in self:
            if record.lot_id:
                return {'value': {'price_unit':record.lot_id.sale_price}}
                # raise UserError()

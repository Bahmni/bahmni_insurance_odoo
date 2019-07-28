from odoo import models, fields, api
import logging
import json
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class claims(models.Model):
    _name = 'insurance.claim'
    _description = 'Claims'
    
    @api.depends('insurance_claim_line.price_total')
    def _claimed_amount_all(self):
        """
        Compute the total amounts of the claim
        """
        _logger.info("Inside _amount_all")
        for claim in self:
            claimed_amount_total = 0.0
            amount_approved_total = 0.0
            
            for line in claim.insurance_claim_line:
                claimed_amount_total += line.price_total
                amount_approved_total += line.amount_approved
                
            claim.update({
                'claimed_amount_total': claimed_amount_total,
                'amount_approved_total': amount_approved_total
            })    
        
    @api.model
    def action_track_status(self):
        '''
            Track Status of the claims
        '''
        _logger.info("action_track_status")
        if self.state == 'submitted':
            raise UserError("Currently this feature is not available")
        
        raise UserError("Claim has not been submitted to be tracked")
    
        
    @api.model
    def print_claim(self):
        '''
            Print Claim
        '''
        _logger.info("print_claim")
        raise UserError("Currently this feature is not available")
        
        
    
    @api.multi
    @api.onchange('sale_orders')
    def onchange_sale_orders_add_claim(self):
        """
        Trigger the change of sale order to add claims for associated sale orders
        """
        _logger.info("onchange_sale_orders_add_claim")
        

    
    @api.multi
    @api.onchange('partner_id')
    def _get_insurance_details(self):
        """
            Get insurance details
        """
        _logger.info("_get_insurance_details")
        insurance_eligibility = self.env['insurance.eligibility'].get_insurance_eligibility(self.partner_id)
    
    @api.multi
    def _create_claim(self, sale_order):
        '''
            Create/Update claims
        '''
        _logger.info("_create_claim")
        _logger.info(sale_order)
        if sale_order and sale_order.payment_type in ('insurance', 'partial'):
            '''
                Create and save claims
            '''
            external_id = sale_order.order_line[0].external_id
            claim_in_db = order_in_db = self.env['insurance.claim'].search([('external_uuid', '=', external_id)])
            if claim_in_db:
                '''Update existing claim'''
                _logger.info("About to edit claim")
                    
                ''' Update contents of claim only if claim is partial or insurance'''
                    
                ''' Update contents of claim line only if payment type is insurance'''
                ''' Check whether a given product has a line item, if yes add quantity, if no add line item'''
                    
                self._update_claim_line(claim_in_db, sale_order)
                    
            else:
                '''Create new claim'''
                _logger.info("About to Create new claim")
                insurance_sale_order_lines = sale_order.order_line.filtered(lambda r: r.payment_type == 'insurance')
                if len(insurance_sale_order_lines) == 0 :
                    raise UserError("No Sales order line marked as Insurance Payment type")
                    
                claim = {
                    'claim_manager_id' : sale_order.user_id.id,
                    'claimed_date' : sale_order.create_date,
                    'partner_id' : sale_order.partner_id.id,
                    'state' : 'draft',
                    'external_uuid' : insurance_sale_order_lines[0].external_id,
                    'partner_uuid' : sale_order.partner_uuid
                }
                
                _logger.info("claim=%s",claim)
                
                try:
                    claim_in_db = self.env['insurance.claim'].create(claim)
                    
                    # Add insurance claim line
                    self._create_claim_line(claim_in_db, sale_order)
                    
                    insurance_claim_lines = self.env['insurance.claim.line'].search([('claim_id', '=', claim_in_db.id)])
                    claim_in_db.update({'insurance_claim_line': insurance_claim_lines})
                    
                    
                    # Add history
                    claim_history_line = self.env['insurance.claim.history']._add_claim_history(claim_in_db)
                    
                    claim_history = self.env['insurance.claim.history'].search([('claim_id', '=', claim_in_db.id)])
                    if claim_history:
                        claim_in_db.update({'insurance_claim_history': claim_history})
                    
                    
                    
                except Exception as err:
                    _logger.info("\n Error Generating claim draft: %s", err)
                    raise UserError(err)
            
    
    def _create_claim_line(self, claim, sale_order):
        _logger.info("Inside _create_claim_line")
        insurance_sale_order_lines = sale_order.order_line.filtered(lambda r: r.payment_type == 'insurance')
        if len(insurance_sale_order_lines) == 0 :
            raise UserError("No Sales order line marked as Insurance Payment type")
        
        for sale_order_line in insurance_sale_order_lines:
            _logger.info("Inside sale_order_line loop")
            imis_mapped_row = self.env['insurance.odoo.product.map'].search([('odoo_product_id', '=', sale_order_line.product_id.id)])
            _logger.debug("imis_mapped_row ->%s", imis_mapped_row)
            
            if imis_mapped_row is None:
                raise UserError("%s is not mapped to insurance product",sale_order_line.product_id.name)
            
            self.create_new_claim_line(claim, sale_order_line, imis_mapped_row)
            
    def _update_claim_line(self, claim, sale_order_line):
        _logger.info("Inside _update_claim_line")
        
        #Check if a product is already present. If yes update quantity
        insurance_claim_line = claim.insurance_claim_line.filtered(lambda r: r.product_id.id == sale_order_line.product_id.id)
       
        if insurance_claim_line:
            insurance_claim_line.update({'product_qty': insurance_claim_line + sale_order_line.product_uom_qty })
        else:
            self._create_claim_line(claim, sale_order_line)
    
    def create_new_claim_line(self, claim, sale_order_line, imis_mapped_row):    
        claim_line_item = {
            'claim_id' : claim.id,
            'product_id' : sale_order_line.product_id.id,
            'product_qty' : sale_order_line.product_uom_qty,
            'product_uom' : sale_order_line.product_uom.id,
            'state' : 'draft',
            'imis_product' : imis_mapped_row.id,
            'imis_product_code' : imis_mapped_row.item_code,
            'price_unit' : imis_mapped_row.insurance_price
        }
        self.env['insurance.claim.line'].create(claim_line_item)
    
    @api.model
    def action_confirm(self):
        '''
            Confirm claim for submission
        ''' 
        #check if state is draft or rejected
        for claim in self:
            if claim.state in ('draft', 'rejected'):
                claim.state = 'confirmed'
                #Check if amount claimed is in the range of eligibility
                
                #Validation passes then confirm
                for claim_line in claim:
                    if claim_line.imis_product_code :
                        claim_line.update({
                            'state': 'confirmed'
                        })
                    else:
                        raise UserError("Product has no mapping present.Map the product and retry again.")
    
    @api.model
    def action_claim_submit(self):
        '''
            Generate the claim number based on the range
            Change status to submitted
            Prepare json
            Submit the claim to insurance-integration
        '''
        _logger.info("_submit_claims")
    
    claim_code = fields.Char(string='Claim Code', help="Claim Code")
    claim_manager_id = fields.Many2one('res.users', string='Claims Manager', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    claimed_date = fields.Datetime(string='Creation Date', index=True, help="Date on which claim is created.")
    claimed_received_date = fields.Datetime(string='Processed Date', index=True, help="Date on which claim is processed.")
    claimed_amount_total = fields.Monetary(string='Total Claimed Amount', store=True, readonly=True, compute='_claimed_amount_all')
    partner_id = fields.Many2one('res.partner', string='Insuree', required=True, change_default=True, index=True, track_visibility='always')
    nhis_number = fields.Char(related='partner_id.nhis_number', readonly=True, store=True, string='NHIS Number')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('insurance.claim'))
    amount_approved_total = fields.Monetary(string='Total Approved Amount', store=True, compute='_claimed_amount_all')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('submitted', 'Submitted'),
        ('rejected', 'Rejected')
        ], string='Claim Status', default='draft', readonly=True)
    claim_comments = fields.Text(string='Comments')
    rejection_reason = fields.Text(string='Rejection Reason')
    insurance_claim_line = fields.One2many("insurance.claim.line", "claim_id", string='Claim Lines', states={'confirmed': [('readonly', True)], 'submitted': [('readonly', True)], 'rejected': [('readonly', True)]}, copy=True)
    sale_orders = fields.Many2many('sale.order', string='Sale Orders')
    external_uuid = fields.Char(string="External Id", help="This field is used to store external id of related sale order")
    partner_uuid = fields.Char(related='partner_id.uuid', string='Customer UUID', store=True, readonly=True)
    currency_id = fields.Many2one(related='sale_orders.currency_id', string="Currency", readonly=True, required=True)
    insurance_claim_history = fields.One2many('insurance.claim.history', 'claim_id', string='Claim Lines', states={'confirmed': [('readonly', True)], 'submitted': [('readonly', True)], 'rejected': [('readonly', True)]}, copy=True)
    insurance_eligibility = fields.Reference(selection=_get_insurance_details, string='Insurance Eligibility')
    

class claims_line(models.Model):
    _name = 'insurance.claim.line'
    _description = 'Claim Line Items' 
    
    @api.depends('product_id')
    def _get_imis_product_code(self):
        _logger.info("Inside _get_imis_product_code")
        product_id = self.product_id.id
        insurance_product_mapper = self.env['insurance.odoo.product.map'].search([('odoo_product_id' , '=', product_id), ('is_active', '=', 't')])
        _logger.info(insurance_product_mapper)
        if insurance_product_mapper:
            self.imis_product = insurance_product_mapper
            self.imis_product_code = insurance_product_mapper.imis_product_code
            self.price_unit = insurance_product_mapper.insurance_price
        else:
            raise UserError("This product has no mapping for insurance products")  
        
    @api.depends('product_id')
    def _get_unit_price(self):
        """
        Get unit price of the ite,
        """
        _logger.info("Inside _get_unit_price")
        self.price_unit = self.product_id.insurance_price
    
    @api.depends('product_qty', 'price_unit', 'product_uom')
    def _compute_amount(self):
        """
        Compute the amounts of the Claim line Item.
        """
        _logger.info("Inside _amount_all")
        self.price_total = self.price_unit * self.product_qty
        
    claim_id = fields.Many2one('insurance.claim', string='Claim ID', required=True, ondelete='cascade', index=True, copy=False)
    claim_manager_id = fields.Many2one(related='claim_id.claim_manager_id', store=True, string='Claims Manager', readonly=True)
    claim_partner_id = fields.Many2one(related='claim_id.partner_id', store=True, string='Customer')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    imis_product = fields.Many2one('insurance.odoo.product.map', string='Insurance Item', change_default=True, required=True)
    imis_product_code = fields.Char(string='Product', change_default=True, required=True)
    product_qty = fields.Float(string='Quantity', required=True, default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float(string='Unit Price', required=True, default=0.0)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    amount_approved = fields.Monetary(string='Approved amount', store=True)
    currency_id = fields.Many2one(related='claim_id.currency_id', string="Currency", readonly=True, required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('submitted', 'Submitted'),
        ('rejected', 'Rejected')
        ], related='claim_id.state', string='Claim Status', readonly=True, copy=False, store=True, default='draft')
    claim_comments = fields.Text(string='Comments')
    rejection_reason = fields.Text(string='Rejection Reason')
    
    
class claim_history(models.Model):
    _name = 'insurance.claim.history'
    _description = 'Claim History'
    
    @api.model
    def _add_claim_history(self, claim):
        _logger.info("Inside _add_claim_history")
        claim_history = {
            'claim_id' : claim.id,
            'partner_id' : claim.partner_id.id,
            'claim_manager_id' : claim.claim_manager_id.id,
            'claim_code' : claim.claim_code,
            'state' : claim.state,
            'claim_comments' : claim.claim_comments,
            'rejection_reason' : claim.rejection_reason
        }
        return self.env['insurance.claim.history'].create(claim_history)
    
    
    claim_id = fields.Many2one('insurance.claim', string='Claim ID', required=True, ondelete='cascade', index=True, copy=False)
    partner_id = fields.Many2one(related='claim_id.partner_id', string='Insuree', readonly=True, required=True, change_default=True, index=True, track_visibility='always')
    claim_manager_id = fields.Many2one(related='claim_id.claim_manager_id', store=True, string='Claims Manager', readonly=True)
    claim_code = fields.Char(related='claim_id.claim_code', store=True, string='Claim Code')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('submitted', 'Submitted'),
        ('rejected', 'Rejected'),
    ], related='claim_id.state', string='Claim Status', readonly=True, copy=False, store=True, default='draft')
    claim_comments = fields.Text(related='claim_id.claim_comments', store=True, string='Claim Comments')
    rejection_reason = fields.Text(related='claim_id.rejection_reason', store=True, string='Rejection Reason')
    
    

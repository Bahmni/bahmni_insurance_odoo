from odoo import models, fields, api
import logging
import json

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
        self.claimed_amount_total = 20
        
    @api.depends('insurance_claim_line.price_total')
    def _approved_amount_all(self):
        """
        Compute the total amounts of the approved claim
        """
        _logger.info("Inside _approved_amount_all")
        self.amount_approved_total = 10
            
    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()
    
    @api.model
    def _submit_claims(self):
        '''
            Generate the claim number based on the range
            Change status to submitted
            Prepare json
            Submit the claim to insurance-integration
        '''
                
    
    claim_code = fields.Char(string='Claim Code', help="Claim Code")
    claim_manager_id = fields.Many2one('res.users', string='Claims Manager', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    claimed_date = fields.Datetime(string='Creation Date', index=True, help="Date on which claim is created.")
    claimed_received_date = fields.Datetime(string='Processed Date', index=True, help="Date on which claim is processed.")
    claimed_amount_total = fields.Monetary(string='Total Claimed Amount', store=True, readonly=True, compute='_amount_all')
    partner_id = fields.Many2one('res.partner', string='Insuree', required=True, change_default=True, index=True, track_visibility='always')
    nhis_number = fields.Char(related='partner_id.nhis_number', readonly=True, store=True, string='NHIS Number')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('insurance.claim'))
    amount_approved_total = fields.Monetary(string='Total Approved Amount', store=True, compute='_approved_amount_all')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('submitted', 'Submitted'),
        ('rejected', 'Rejected')
        ], string='Claim Status', readonly=True)
    claim_comments = fields.Text(string='Comments')
    rejection_reason = fields.Text(string='Rejection Reason')
    pricelist_id = fields.Many2one('product.pricelist', String='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Pricelist for current claims")
    currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True, required=True)
    insurance_claim_line = fields.One2many("insurance.claim.line", "claim_id", string='Claim Lines', states={'confirmed': [('readonly', True)], 'submitted': [('readonly', True)], 'rejected': [('readonly', True)]}, copy=True)
    sale_orders = fields.Many2many('sale.order', string='Sale Orders')



class claims_line(models.Model):
    _name = 'insurance.claim.line'
    _description = 'Claim Line Items' 
    
    
    @api.depends('product_id')
    def _get_imis_product_code(self):
        _logger.info("Inside _get_imis_product_code")
        product_id = self.product_id.id
        insurance_product_mapper = self.env['insurance.odoo.product.map'].search([('odoo_product_id' , '=', product_id),('is_active', '=', 't')])
        _logger.info(insurance_product_mapper)
        if insurance_product_mapper:
            self.imis_product = insurance_product_mapper
            self.claim_code = insurance_product_mapper.code
        
    
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
    imis_product = fields.Many2one('insurance.odoo.product.map', string='Insurance Item', change_default=True, ondelete='restrict', required=True)
    imis_product_code = fields.Many2one('insurance.odoo.product.map', string='Product', change_default=True, ondelete='restrict', required=True)
    product_qty = fields.Float(string='Quantity', required=True, default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float('Unit Price', required=True, default=0.0)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    amount_approved = fields.Monetary(string='Approved amount', store=True)
    currency_id = fields.Many2one(related='claim_id.currency_id', store=True, string='Currency', readonly=True)
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
    claim_comments =  fields.Text(related='claim_id.claim_comments', store=True, string='Claim Comments')
    rejection_reason = fields.Text(related='claim_id.rejection_reason', store=True,string='Rejection Reason')
    
    
    
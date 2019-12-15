# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools import drop_view_if_exists
from odoo.exceptions import Warning


class claim_report(models.Model):
    _name = "claim.report"
    _description = "Claim Report"
    _auto = False
    _order = 'claimed_date desc'

    partner_id = fields.Many2one('res.partner', string='Insuree')
    claim_code = fields.Text(string="Claim ID", readonly=True)
    claimed_amount_total = fields.Float(string='Total Claimed Amount')
    amount_approved_total = fields.Float(string='Total Approved Amount', store=True)
    nhis_number = fields.Char(string='NHIS Number')
    state = fields.Text(string="Status")
    claimed_date = fields.Datetime(string="Claimed Date")
    
    
    @api.model_cr
    def init(self):
        drop_view_if_exists(self.env.cr, 'claim_report')
        self.env.cr.execute("""
            create or replace view claim_report as (
                SELECT
                  row_number() OVER () AS id,
                  clm.partner_id,
                  clm.claim_code,
                  clm.claimed_amount_total,
                  clm.amount_approved_total,
                  clm.nhis_number,
                  clm.state,
                  clm.claimed_date
                FROM insurance_claim clm
            )""")

    @api.multi
    def unlink(self):
        raise Warning('You cannot delete any record!')

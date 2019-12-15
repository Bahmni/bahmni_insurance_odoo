# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools import drop_view_if_exists
from odoo.exceptions import Warning


class claim_patient_report(models.Model):
    _name = "claim.patient.report"
    _description = "Claim Patient Report"
    _auto = False
    _order = 'total_claims desc'

    partner_id = fields.Many2one('res.partner', string='Insuree')
    nhis_number = fields.Char(string='NHIS Number')
    total_claims = fields.Integer(string='Total Claims')
    claimed_amount_total = fields.Float(string='Total Claimed Amount')
    total_under_review_claims = fields.Integer(string='Total Under Review Claims')
    amount_under_review_claims = fields.Integer(string='Total Under Review Amount')
    total_approved_claims = fields.Integer(string='Total Approved Claims')
    amount_approved_total = fields.Float(string='Total Approved Amount')
    total_rejected_claims = fields.Integer(string='Total Rejected Claims')
    amount_rejected_total = fields.Float(string='Total Rejected Claims')
    
    
    @api.model_cr
    def init(self):
        drop_view_if_exists(self.env.cr, 'claim_patient_report')
        self.env.cr.execute("""
            create or replace view claim_patient_report as (
                SELECT
                  row_number() OVER () AS id,
                  clm.partner_id,
                  clm.nhis_number,
                  count(clm.id) as total_claims,
                  SUM(clm.claimed_amount_total) as claimed_amount_total,
                  COUNT(CASE WHEN clm.state ='checked' THEN 
                    clm.id
                  ELSE
                    NULL
                  END) as total_under_review_claims,
                  SUM(CASE WHEN clm.state ='checked' THEN
                    clm.claimed_amount_total 
                  ELSE
                    0
                  END) as amount_under_review_claims,
                  COUNT(CASE WHEN clm.state ='valuated' THEN
                   clm.id
                  ELSE
                    NULL
                  END) as total_approved_claims,
                  SUM(CASE WHEN clm.state ='valuated' THEN 
                    clm.claimed_amount_total
                  ELSE
                    0
                  END) as amount_approved_total,
                  COUNT(CASE WHEN clm.state ='rejected' THEN 
                   clm.id
                  ELSE
                    NULL
                  END) as total_rejected_claims,
                  SUM(CASE WHEN clm.state ='rejected' THEN  
                    clm.claimed_amount_total
                  ELSE
                    0 
                  END) as amount_rejected_total
                FROM insurance_claim clm
                WHERE clm.state in ('checked', 'valuated', 'rejected')
                  
                GROUP BY
                  clm.partner_id,
                  clm.nhis_number
            )""")

    @api.multi
    def unlink(self):
        raise Warning('You cannot delete any record!')

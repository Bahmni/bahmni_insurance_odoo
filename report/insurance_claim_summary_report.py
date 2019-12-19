# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools import drop_view_if_exists
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class insurance_claim_summary_report(models.AbstractModel):
    _name = "report.bahmni_insurance_odoo.insurance_claim_summary"
    _description = "Claim Details Report"
    
    @api.model
    def render_html(self, docids, data=None):
        _logger.debug("Inside get_report_values \n\n")
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        
        
        report_lines = self.get_insurance_details(date_start, date_end)
        
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'date_start': date_start,
            'date_end': date_end,
            'report_lines': report_lines
        }
        
        return self.env['report'].render('bahmni_insurance_odoo.insurance_claim_summary', docargs)
        
#         return data
    
    @api.model
    def get_insurance_details(self, date_start=False, date_end=False):
        """ Get Claim information For given data range

        params: date_start, date_end
        """
        
        _logger.debug("Inside get_insurance_details \n\n")
        
        query = """
            SELECT
                row_number() OVER () AS id,
                COUNT(patient_insurance_report.partner_id) AS total_insuree,
                SUM(patient_insurance_report.total_claims) AS total_claims,
                SUM(patient_insurance_report.claimed_amount_total) as claimed_amount_total,
                SUM(patient_insurance_report.total_under_review_claims) AS total_under_review_claims,
                SUM(patient_insurance_report.amount_under_review_claims) AS amount_under_review_claims,
                SUM(patient_insurance_report.total_approved_claims) AS total_valuated_claims,
                SUM(patient_insurance_report.amount_approved_total) AS amount_valuated_total,
                SUM(patient_insurance_report.total_rejected_claims) AS total_rejected_claims,
                SUM(patient_insurance_report.amount_rejected_total) AS amount_rejected_total,
                SUM(patient_insurance_report.total_draft_claims) AS total_draft_claims,
                SUM(patient_insurance_report.amount_draft_total) AS amount_draft_total
            FROM (
                SELECT
                    clm.partner_id AS partner_id,
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
                    END) as amount_rejected_total,
                    COUNT(CASE WHEN clm.state ='draft' or clm.state ='confirmed' or clm.state = 'submitted' THEN 
                       clm.id
                      ELSE
                        NULL
                    END) as total_draft_claims,
                    SUM(CASE WHEN clm.state ='draft' or clm.state ='confirmed' or clm.state = 'submitted' THEN  
                        clm.claimed_amount_total
                      ELSE
                        0 
                    END) as amount_draft_total
                FROM insurance_claim clm
                WHERE clm.create_date BETWEEN %s AND %s
                GROUP BY
                    clm.partner_id
                ) patient_insurance_report
            """
        
        params = (date_start, date_end)
        
        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        
        _logger.debug(result)
        
        return result
            
#         return {
#             'total_insuree': result[0],
#             'total_claims': result[1],
#             'claimed_amount_total': result[2],
#             'total_under_review_claims': result[3],
#             'amount_under_review_claims': result[4],
#             'total_valuated_claims': result[5],
#             'amount_valuated_total': result[6],
#             'total_rejected_claims': result[7],
#             'amount_rejected_total': result[8],
#             'total_draft_claims': result[9],
#             'amount_draft_total' : result[10]
#         }

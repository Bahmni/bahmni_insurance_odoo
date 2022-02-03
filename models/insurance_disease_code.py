from odoo import models, fields, api
import logging
import json

_logger = logging.getLogger(__name__)
class insurance_disease_code(models.Model):
    _name = 'insurance.disease.code'
    
    ipdCode = fields.Char(string="ICD Code", help="This field is used to code of the disease as in IPD", required=True)
    diagnosis = fields.Char(string="Diagnosis", help="This field is used to store disease", required=True)
    is_active = fields.Boolean(string="Is active")    

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = record.ipdCode + ' - ' + record.diagnosis
            result.append((record.id, record_name))
        return result
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search([('diagnosis', operator, name)] + args, limit=limit)
        return recs.name_get()
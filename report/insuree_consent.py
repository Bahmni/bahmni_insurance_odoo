from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class insuree_consent(models.TransientModel):
    _name = 'insuree.consent'
    
    name = fields.Char('Insuree Name', readonly=True)
    nhis_number = fields.Char('NHIS Number', readonly=True)
    company_name = fields.Char('Company Name', readonly=True)
    
    @api.model
    def _something(self):
        _logger.info("\n\n\n\n===================")
        _logger.info("Inside _something")
        self.name="Dipak thapa"
        self.nhis_number="123123123"
        self.company_name="Nyaya Health Nepal"
#         partner_id = self.partner_id
#         _logger.info(partner_id)
        
    
    @api.one
    def init(self):
        _logger.info("\n\n\n\n===================")
        _logger.info("Inside init")
        self._something()
        
    
insuree_consent()
import json
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class OrderSaveService(models.Model):
    _name = 'order.save.service'
    _inherit = 'order.save.service'
    
    
    @api.model
    def create_orders(self, vals):
        _logger.info("Inside overwritten create_orders")
        all_orders = super(OrderSaveService, self)._get_openerp_orders(vals)

        if not all_orders:
            return ""
        visit_uuid = all_orders[0].get("visitId")
        encounter_uuid = vals.get("encounter_id")
        super(OrderSaveService, self).create_orders(vals)
        
        #Search Sale order line based on encounter id
        sale_order_lines_in_db = self.env['sale.order.line'].search([('external_id', '=', encounter_uuid)])
        
        if sale_order_lines_in_db:
            _logger.info('Sale order line found')
            sale_order = self.env['sale.order'].search(('id', '=', sale_order_lines_in_db[0].order_id))
            sale_order.update({
                'external_visit_uuid': visit_uuid
            })

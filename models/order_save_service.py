import json
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class OrderSaveService(models.Model):
    _name = 'order.save.service'
    _inherit = 'order.save.service'

    payment_type='cash'

    def getInsuranceCost(self,productData):
        # resData = self.env('insurance.odoo.product.map').search(self._cr, self._uid, [( 'odoo_product_id', 'in', productData.id) ])
        resData =self.env['insurance.odoo.product.map'].search([('odoo_product_id', '=', productData.id)], limit=10)
        # raise UserError(_('getting insurance cost of '+ str(len(resData))))
        if len(resData) == 0:
            return productData.list_price
            # raise UserError(_('Product not found in mapping. Please contact admin.'))
            # return {'warning': {'title':'Warning!!!','message':'Product not found in mapping. Please contact admin.'},'value': {'payment_type': 'cash'}}
        else:
            return resData[0].insurance_price
    
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
        
        customer_id = vals.get("customer_id")
        customer_ids = self.env['res.partner'].search([('ref', '=', customer_id)])
        if customer_ids:
            cus_id = customer_ids[0]
            if cus_id.nhis_number:
                    self.payment_type= 'insurance'
        if sale_order_lines_in_db:
            _logger.info('Sale order line found')
            sale_order = sale_order_lines_in_db[0].order_id
            _logger.info(sale_order)
            sale_order.update({
                'external_visit_uuid': visit_uuid,
                'payment_type': self.payment_type,
            })
            for sale_order_line in sale_order_lines_in_db:
                if self.payment_type == 'insurance':
                    insurance_cost = self.getInsuranceCost(sale_order_line.product_id)
                    sale_order_line.update({
                        'payment_type': self.payment_type,
                        'price_unit':insurance_cost
                    })
                else:
                    sale_order_line.update({
                        'payment_type': self.payment_type
                    })

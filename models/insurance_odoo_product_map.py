from odoo import models, fields, api
import logging
import json

_logger = logging.getLogger(__name__)
class insurance_odoo_product_map(models.Model):
    _name = 'insurance.odoo.product.map'
    
    item_code = fields.Char(string="Item Code", help="This field is used to store item code item in Insurance System", required=True)
    insurance_product = fields.Char(string="Insurance Product Name", help="This field is used to store product in Insurance System", required=True)
    insurance_price = fields.Float(string="Insurance Product Price", help="This field is used to store Insurance product price in Insurance System", required=True)
    odoo_product_id = fields.Many2one('product.product', string="Odoo Product")
    valid_from = fields.Datetime(string="Valid From")
    valid_till = fields.Datetime(string="Valid Till")
    is_active = fields.Boolean(string="Is active")    
    
    
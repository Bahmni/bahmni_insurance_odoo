from odoo import models, fields, api
import logging
import json

_logger = logging.getLogger(__name__)
class imis_odoo_product_map(models.Model):
    _name = 'imis.odoo.product.map'

    item_code = fields.Char(string="Item Code", help="This field is used to store item code item in openimis", required=True)
    imis_product = fields.Char(string="Imis Product Name", help="This field is used to store product in openimis", required=True)
    imis_price = fields.Float(string="Imis Product Price", help="This field is used to store imis product price in openimis", required=True)
    odoo_product_id = fields.Many2one('product.product', string="Odoo Product")
    valid_from = fields.Datetime(string="Valid From")
    valid_till = fields.Datetime(string="Valid Till")
    is_active = fields.Boolean(string="Is active")

    @api.onchange('is_active')
    def try_something(self):
        _logger.info("Inside try_something")
        self.env['imis.connect'].authenticate("admin", "haha", "https://192.168.33.20/insurance-integration/patient/e7a6efb4-1dfb-4e84-87dd-45b8fb920ceb")
        


imis_odoo_product_map()
    
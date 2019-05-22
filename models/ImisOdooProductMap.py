from odoo import models, fields

class ImisOdooProductMap(models.Model):
    _name = 'imis.odoo.product.map'

    item_code = fields.Char(string="Item Code", help="This field is used to store item code item in openimis", required=True)
    imis_product = fields.Char(string="Imis Product Name", help="This field is used to store product in openimis", required=True)
    imis_price = fields.Float(string="Imis Product Name", help="This field is used to store product in openimis", required=True)
    odoo_product_id = fields.Many2one('product.product', string="Odoo Product")
    valid_from = fields.Date(string="Valid From")
    valid_till = fields.Date(string="Valid Till")
    is_active = fields.Boolean(string="Is active")


ImisOdooProductMap()
    
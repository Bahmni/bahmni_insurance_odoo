from odoo import models, fields

class imis_config(models.Model):
    _name = 'imis.config'

    name = fields.Char(string="Naame", required=True)
    value = fields.Char(string="Value", required=True)
    imis_price = fields.Char(string="Description")

imis_config()
    
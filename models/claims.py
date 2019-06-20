from odoo import models, fields, api
import logging
import json

_logger = logging.getLogger(__name__)
class claims(models.TransientModel):
    _name = 'insurance.claims'
    
    
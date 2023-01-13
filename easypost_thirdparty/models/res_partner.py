
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shipping_payment_account = fields.Char(string='Shipment Account Number', size=100)


from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipping_payment_type = fields.Selection([
        ('SENDER', 'Sender'), ('THIRD_PARTY', 'Third Party'), ('RECEIVER', 'Receiver')], default='SENDER')
    shipping_thirdparty_partner_id = fields.Many2one('res.partner', 'Payment Partner')

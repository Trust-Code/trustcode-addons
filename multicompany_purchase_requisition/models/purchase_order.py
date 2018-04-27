from odoo import models, fields
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    centralizador_id = fields.Many2one(
        'purchase.multicompany.req', string="Centralizador"
    )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_increment = fields.Float(
        string='Qty Increment', digits=dp.get_precision(
            'Product Unit of Measure'))

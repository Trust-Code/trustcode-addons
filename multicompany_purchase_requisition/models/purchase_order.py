from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    centralizador_id = fields.Many2one(
        'to.be.defined', string="Centralizador"
    )

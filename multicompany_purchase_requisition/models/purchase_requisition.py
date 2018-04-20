from odoo import models, fields


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    centralizador_id = fields.Many2one(
        'to.be.defined', string="Centralizador"
    )

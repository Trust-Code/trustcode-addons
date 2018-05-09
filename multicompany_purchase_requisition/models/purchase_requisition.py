from odoo import models, fields


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    centralizador_id = fields.Many2one(
        'purchase.multicompany.req', string="Centralizador"
    )

from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    additional_info = fields.Text()

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_support_contract = fields.Boolean(string="Contrato de Suporte?")
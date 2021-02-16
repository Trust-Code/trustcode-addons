from odoo import fields, models


class BoletoCloud(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(selection_add=[("boleto.cloud", "Boleto Cloud")])


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    boleto_pdf = fields.Binary(string="Boleto PDF")

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('payment_move_line_ids.amount_residual')
    def _compute_last_payment(self):
        for invoice in self:
            for payment in invoice.payment_move_line_ids:
                invoice.last_payment_date = payment.date
                break

    last_payment_date = fields.Date(
        string="Último pagamento", compute='_compute_last_payment', store=True)

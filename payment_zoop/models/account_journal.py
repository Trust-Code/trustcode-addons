# © 2020 Danimar Ribeiro, Trustcode
# Part of Trustcode. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_acquirer_id = fields.Many2one("payment.acquirer", string="Provedor de pagamento")


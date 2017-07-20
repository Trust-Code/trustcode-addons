# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Royalties(models.TransientModel):
    _name = "royalties.wizard"

    royalties_ids = fields.Many2many('royalties',
                                     string='Contratos',
                                     domain="[('state','in', \
                                     ['in_progress','done'])]",)

    def run_royalties_payment(self):
        account_royalties_line = self.env['account.royalties.line']
        account_royalties_line.get_invoice_royalties(self.royalties_ids)
        if self.royalties_ids:
            self.royalties_ids.royalties_payment()

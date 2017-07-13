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
        if self.royalties_ids:
            self.royalties_ids.royalties_payment()
        else:
            self.royalties_ids.search([('state', 'in',
                                       ['in_progress', 'done'])])

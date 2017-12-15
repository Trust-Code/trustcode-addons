# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models

class SaleContractMerge(models.TransientModel):
    _name = 'sale.contract.merge'

    def merge_selected_contracts(self):
        active_ids = self.env.context.get('active_ids', [])
        self.env['sale.order'].merge_contracts(active_ids)
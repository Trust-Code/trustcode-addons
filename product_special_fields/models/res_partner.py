# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_open_product_lot(self):
        self.ensure_one()
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('partner_id', '=', self.id)]
        return action

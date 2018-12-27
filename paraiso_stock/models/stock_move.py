# -*- coding: utf-8 -*-
# © 2018, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    stock_state = fields.Char(string="Move color", compute='_set_color')

    @api.multi
    def _set_color(self):
        for move in self:
            qty = move.product_id.virtual_available - move.product_uom_qty
            if qty >= 0:
                move.stock_state = 'green'
            elif qty < 0:
                move.stock_state = 'red'

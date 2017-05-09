# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_reserve(self, quants, move, link=False):
        res = super(StockQuant, self).quants_reserve(quants, move, link=link)
        for quant in quants:
            if quant[0] and move.picking_id.owner_id:
                quant[0].sudo().write(
                    {'owner_id': move.picking_id.owner_id.id})
        return res

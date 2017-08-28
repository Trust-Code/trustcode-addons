# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMoveDemand(models.Model):
    _inherit = 'stock.move'

    is_procurement_on_demand = fields.Boolean(name="is proc. on demand?")

    @api.multi
    def action_assign(self, no_prepare=False):
        res = super(StockMoveDemand, self).action_assign()
        procurement_obj = self.env['procurement.order']

        for move in self:
            vrt_available = move.product_id.virtual_available + \
                move.product_uom_qty
            if move.location_dest_id.usage in ('customer', 'production') and \
               move.procure_method == 'make_to_stock' and \
               move.product_id.nbr_reordering_rules == 0 and \
               move.state == 'confirmed' and \
               not move.is_procurement_on_demand and \
               vrt_available < move.product_uom_qty:

                move.route_ids = move.product_id.mapped('route_ids')
                if move.route_ids:
                    vals = move._prepare_procurement_from_move()
                    vals['product_qty'] = move.product_uom_qty - vrt_available
                    vals['name'] = vals['name'] + ' (Stock on demand rule)'
                    procurement_obj.create(vals)
                move.is_procurement_on_demand = True

        return res

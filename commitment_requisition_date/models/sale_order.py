# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date = fields.Datetime(track_visibility='onchange')
    requested_date = fields.Datetime(track_visibility='onchange')
    observation_order_sale = fields.Text('Observation')

    def _sale_order_dates_update(self, vals):
        if self.procurement_group_id:
            mrp_production = self.env['mrp.production'].search([
                ('procurement_group_id', '=', self.procurement_group_id.id)])
            for production in mrp_production:
                production.update({
                    'commitment_date': vals.get('commitment_date'),
                    'requisition_date': vals.get('requested_date'),
                    'observation_order_sale':  vals.get('observation_order_sale'),
                    })

        picking_ids = self.picking_ids.filtered(lambda x: x.state != 'cancel')

        for picking in picking_ids:
            picking.update({
                'commitment_date': vals.get('commitment_date'),
                'requisition_date': vals.get('requested_date'),
                'observation_order_sale':  vals.get('observation_order_sale'),
            })

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if any(item in vals for item in ['commitment_date', 'requested_date', 'observation_order_sale']):
            self._sale_order_dates_update({
                'commitment_date': vals.get('commitment_date'),
                'requested_date': vals.get('requested_date'),
                'observation_order_sale': vals.get('observation_order_sale'),
            })
        return res


    @api.multi
    def action_confirm(self):
        for sale_order in self:
            res = super(SaleOrder, self).action_confirm()

            observation_order_sale = sale_order.observation_order_sale

            if observation_order_sale:
                move_ids = self.picking_ids.filtered(
                    lambda x: x.state != 'cancel')
                for move in move_ids:
                    move.write({'observation_order_sale': observation_order_sale})
            return res

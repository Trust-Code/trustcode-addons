# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _sale_order_dates_update(self, vals):
        if self.procurement_group_id:
            mrp_production = self.env['mrp.production'].search([
                ('procurement_group_id', '=', self.procurement_group_id.id)])
            for production in mrp_production:
                production.write({
                    'commitment_date': vals.get('commitment_date'),
                    'requisition_date': vals.get('requested_date'),
                    })

        picking_ids = self.picking_ids.filtered(lambda x: x.state != 'cancel')

        for picking in picking_ids:
            picking.write({
                'commitment_date': vals.get('commitment_date'),
                'requisition_date': vals.get('requested_date'),
            })

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if any(item in vals for item in ['commitment_date', 'requested_date']):
            self._sale_order_dates_update({
                'commitment_date': vals.get('commitment_date'),
                'requested_date': vals.get('requested_date'),
            })
        return res

# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date = fields.Datetime(track_visibility='onchange')
    requested_date = fields.Datetime(track_visibility='onchange')
    observation_sale_order = fields.Text(
        'Observation', track_visibility='onchange')

    @api.onchange('observation_sale_order')
    def _update_observation(self):
        for pcking in self.picking_ids.filtered(lambda p: p.state != 'cancel'):
            pcking.write(
                {'observation_sale_order': self.observation_sale_order})

        mrp_production = self.env['mrp.production'].search([
                ('procurement_group_id', '=', self.procurement_group_id.id)])
        for production in mrp_production:
            production.write(
                {'observation_sale_order': self.observation_sale_order})

    def _sale_order_dates_update(self, vals):
        if self.procurement_group_id:
            mrp_production = self.env['mrp.production'].search([
                ('procurement_group_id', '=', self.procurement_group_id.id)])
            for production in mrp_production:
                production.update({
                    'commitment_date': vals.get('commitment_date'),
                    'requisition_date': vals.get('requested_date')
                })

        for pcking in self.picking_ids.filtered(lambda p: p.state != 'cancel'):
            pcking.write({
                'commitment_date': vals.get('commitment_date'),
                'requisition_date': vals.get('requested_date')
            })

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if any(item in vals for item in ['commitment_date', 'requested_date']):
            self._sale_order_dates_update({
                'commitment_date': vals.get('commitment_date'),
                'requested_date': vals.get('requested_date')
            })
        return res

    @api.multi
    def action_update_observation(self):
        return {
            'name': 'Update Observation',
            'type': 'ir.actions.act_window',
            'res_model': 'update.observation.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'old_observation': self.observation_sale_order,
            }
        }

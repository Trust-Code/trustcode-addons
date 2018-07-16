# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    commitment_date = fields.Datetime(
        'Data do Compromisso', track_visibility='onchange')
    requisition_date = fields.Datetime(
        'Data do Requisição', track_visibility='onchange')
    observation_order_sale = fields.Text('observations')


    @api.multi
    def update_sale_order_observation(self):
        sale_order = self.env['sale.order'].search([
            ('procurement_group_id', '=', self.procurement_group_id.id)])

        return {
            'name': 'Update Observation',
            'type': 'ir.actions.act_window',
            'res_model': 'observation_order_sale',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': sale_order.id
            }
        }

        sale_order.update({
            'observation_order_sale': vals.get('observation_order_sale'),
        })

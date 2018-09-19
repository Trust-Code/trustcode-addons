# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    commitment_date = fields.Datetime(
        'Data do Compromisso', track_visibility='onchange')
    requisition_date = fields.Datetime(
        'Data do Requisição', track_visibility='onchange')
    observation_sale_order = fields.Text(
        'Observations', track_visibility='onchange')
    sale_id = fields.Many2one('sale.order',
                              related='procurement_group_id.sale_id')

    @api.multi
    def action_update_observation(self):
        sale_order = self.env['sale.order'].browse(
            self.procurement_group_id.sale_id.id)

        if not sale_order:
            raise UserError(_(u'Ordem de venda não definido. Para editar \
este campo, por favor, clique em editar, modifique e depois salve.'))

        return {
            'name': 'Update Observation',
            'type': 'ir.actions.act_window',
            'res_model': 'update.observation.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': sale_order.id,
                'old_observation': self.observation_sale_order,
            }
        }

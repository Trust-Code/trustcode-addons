# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    commitment_date = fields.Datetime(
        'Data do Compromisso', track_visibility='onchange')
    requisition_date = fields.Datetime(
        'Data da Requisição', track_visibility='onchange')
    observation_sale_order = fields.Text(
        'Observation')

    @api.multi
    def action_update_observation(self):
        if not self.sale_id:
            raise UserError(_(u'Ordem de venda não definida. Para editar \
este campo, por favor, clique em editar, modifique e depois salve.'))

        return {
            'name': 'Update Observation',
            'type': 'ir.actions.act_window',
            'res_model': 'update.observation.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.sale_id.id,
                'old_observation': self.observation_sale_order,
            }
        }

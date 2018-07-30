# -*- coding: utf-8 -*-
# © 2018 Guilherme Lenon da Silva <Guilhermelds@gmail.com>, Trustcode
# © 2018 Johny Chen Jy<johnychenjy@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class UpdateObservationWizard(models.TransientModel):
    _name = 'update.observation.wizard'

    def _get_old_observation(self):
        old_obs = self.env.context.get('old_observation')
        return old_obs

    old_observation = fields.Text(
        'Observação Antiga', default=_get_old_observation,
        readonly="1")
    new_observation = fields.Text('Nova Observação')

    def action_update_obs(self):
        sale_order = self.env['sale.order'].browse(
            self.env.context.get('default_order_id'))

        # O write do SO vai modificar o campo pra todo mundo
        sale_order.write({
            'observation_sale_order': self.new_observation
            })

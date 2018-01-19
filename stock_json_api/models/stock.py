# -*- encoding: utf-8 -*-
# © 2018 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    def get_action_picking_tree_draft(self):
        return self._get_action('stock_json_api.action_picking_tree_draft')

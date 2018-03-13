# -*- encoding: utf-8 -*-
# © 2018 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    next_picking_type_id = fields.Many2one(
        string="Sequência do processo",
        comodel_name="stock.picking.type",
        help="Picking Type no qual será gerado o picking que dá sequência \
ao processo.")

    def get_action_picking_tree_draft(self):
        return self._get_action('stock_json_api.action_picking_tree_draft')

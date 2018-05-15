# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    material_project_task_id = fields.Many2one(
        'project.task.material', 'Material Task Item')

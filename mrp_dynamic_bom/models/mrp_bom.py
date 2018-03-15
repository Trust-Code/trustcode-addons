# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    default = fields.Boolean(string='Default')

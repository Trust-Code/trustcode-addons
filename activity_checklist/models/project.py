# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class Task(models.Model):
    _inherit = 'project.task'

    checklist_id = fields.Many2one('activity.checklist', 'Checklist')

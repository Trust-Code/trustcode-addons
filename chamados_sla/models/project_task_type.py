# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    block_stages_changes = fields.Boolean(
        'Bloquear mudança de estado',
        help='Marque esta opção se deseja que os incidentes não possam ser\
        movidos desta coluna.')

# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class Project(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        project = super(Project, self).create(vals)
        self._set_default_project_status(project)
        return project

    def _set_default_project_status(self, project):
        type_ids = self.env['project.task.type'].search(
            [('default', '=', True)])
        for item in type_ids:
            item.write({"project_ids": [(4, project.id)]})

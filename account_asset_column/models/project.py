# -*- coding: utf-8 -*-
# © 2018 Marina Domingues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    asset_line_ids = fields.One2many(
        'account.asset.asset', 'project_id', string="Asset lines",
        compute="_compute_asset_lines", store=True)

    def _compute_asset_lines(self):
        self.asset_line_ids = self.env['account.asset.asset'].search([
            ('project_id', '=', self.id)]).ids

# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    kk_site_id = fields.Many2one('kk.sites', string="Site")

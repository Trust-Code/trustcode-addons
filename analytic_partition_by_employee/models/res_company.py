# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        res = super(ResCompany, self).create(vals)
        if res.parent_id:
            res.partner_id.is_branch = True
        return res

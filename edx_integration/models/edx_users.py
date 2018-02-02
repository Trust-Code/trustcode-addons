# -*- encoding: utf-8 -*-
# © 2018 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EdxUsers(models.Model):
    _name = 'edx.users'

    username = fields.Char()
    password = fields.Char()
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        ondelete="set null",
    )

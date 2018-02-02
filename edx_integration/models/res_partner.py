# -*- encoding: utf-8 -*-
# © 2018 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    edx_username = fields.Char()
    edx_password = fields.Char()
    edx_active = fields.Boolean(string="Ativo no EDX")

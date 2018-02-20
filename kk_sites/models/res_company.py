# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    egnyte_host = fields.Char(string="Host Egnyte")
    egnyte_user = fields.Char(string="Usuário Egnyte")
    egnyte_user = fields.Char(string="Senha Egnyte")
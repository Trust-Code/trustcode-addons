# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    egnyte_host = fields.Char(string="Host Egnyte")
    egnyte_acess_token = fields.Char(string="Chave de Acesso Egnyte",
                                     copy=False)
    egnyte_api = fields.Char(string='Api Key')
    egnyte_active = fields.Boolean(string="Criar Pastas no Egnyte",
                                   default=True)

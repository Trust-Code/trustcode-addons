# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FabricanteTorre(models.Model):
    _name = 'kk.fabricante.torre'

    name = fields.Char(string="Nome")

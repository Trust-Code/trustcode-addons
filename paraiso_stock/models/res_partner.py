# -*- coding: utf-8 -*-
# © 2018, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    entregador = fields.Boolean(string="É entregador")

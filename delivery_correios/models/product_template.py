# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    altura = fields.Float(string='Altura')
    largura = fields.Float(string='Largura')
    diametro = fields.Float(string='Diametro')
    comprimento = fields.Float(string='Comprimento')

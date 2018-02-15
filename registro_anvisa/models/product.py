# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.template'

    registro_anvisa = fields.Char(string=u'Registro Anvisa', size=30)
    validade_anvisa = fields.Date(string=u'Validade Anvisa')
    esterilizacao = fields.Char(string=u"Método Esterilizacao", size=100)

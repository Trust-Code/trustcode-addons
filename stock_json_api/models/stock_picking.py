# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    amount_total = fields.Float(string="Valor Total", readonly=True)

    discount = fields.Float(string='Desconto')

    transporte = fields.Float(string='Transporte')

    embalagem = fields.Float(string='Embalagem')

    caixa = fields.Boolean(string='Caixa')
    cesta = fields.Boolean(string='Cesta')
    sacola = fields.Boolean(string='Sacola')
    caixa_ovo = fields.Boolean(string='Caixa de Ovo')
    morango = fields.Boolean(string='Morango')
    cesta_retornavel = fields.Boolean(string='Cesta Retornável')


class StockMove(models.Model):
    _inherit = 'stock.move'

    valor_bruto = fields.Float(string="Valor bruto", readonly=True)

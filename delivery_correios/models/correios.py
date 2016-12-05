# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CorreiosServicos(models.Model):
    _name = 'delivery.correios.service'

    code = fields.Char(string="Código", size=20)
    identifier = fields.Char(string="Identificador", size=20)
    name = fields.Char(string="Descrição", size=70)
    delivery_id = fields.Many2one('delivery.carrier', string="Método entrega")


class CorreiosPostagemPlp(models.Model):
    _name = 'delivery.correios.postagem.plp'

    name = fields.Char(string="Descrição", size=20)
    delivery_id = fields.Many2one('delivery.carrier', string="Método entrega")
    total_value = fields.Float(string="Valor Total")


class CorreiosPostagemObjeto(models.Model):
    _name = 'delivery.correios.postagem.objeto'

    name = fields.Char(string="Descrição", size=20)
    postagem_id = fields.Many2one(
        'delivery.correios.postagem.plp', string="Postagem")
    stock_pack_id = fields.Many2one(
        'stock.pack.operation', string="Item Entrega")

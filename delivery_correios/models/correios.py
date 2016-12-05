# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CorreiosServicos(models.Model):
    _name = 'delivery.correios.service'

    code = fields.Char(string="Código", size=20)
    identifier = fields.Char(string="Identificador", size=20)
    name = fields.Char(string="Descrição", size=70)
    delivery_id = fields.Many2one('delivery.carrier', string="Método entrega")


class CorreiosPostagemPlp(models.Model):
    _name = 'delivery.correios.postagem.plp'

    name = fields.Char(string="Descrição", size=20)
    state = fields.Selection([('draft', 'Rascunho'), ('done', 'Enviado')],
                             string="Status")
    delivery_id = fields.Many2one('delivery.carrier', string="Método entrega")
    total_value = fields.Float(string="Valor Total")
    postagem_id = fields.One2many('delivery.correios.postagem.objeto',
                                  'plp_id', 'Postagens')


class CorreiosPostagemObjeto(models.Model):
    _name = 'delivery.correios.postagem.objeto'

    name = fields.Char(string="Descrição", size=20)
    stock_pack_id = fields.Many2one(
        'stock.pack.operation', string="Item Entrega")
    plp_id = fields.Many2one('delivery.correios.postagem.plp', 'PLP')
    eventos_id = fields.One2many(
        'delivery.correios.postagem.eventos',
        'postagem_id', 'Eventos')


class CorreiosEventosObjeto(models.Model):
    _name = 'delivery.correios.postagem.eventos'

    etiqueta = fields.Char(string='Etiqueta')
    postagem_id = fields.Many2one(
        'delivery.correios.postagem.objeto', 'Postagem')
    status = fields.Char(string='Status')
    data = fields.Date(string='Data')
    local_destino = fields.Char(string='Local Destino')
    local_origem = fields.Char(string='Local Origem')
    descricao = fields.Char(string='Descrição')

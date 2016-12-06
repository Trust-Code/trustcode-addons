# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CorreiosServicos(models.Model):
    _name = 'delivery.correios.service'

    code = fields.Char(string=u"Código", size=20)
    identifier = fields.Char(string=u"Identificador", size=20)
    name = fields.Char(string=u"Descrição", size=70, required=True)
    delivery_id = fields.Many2one('delivery.carrier', string=u"Método entrega")
    chancela = fields.Binary(string='Chancela')
    ano_assinatura = fields.Char(string="Ano Assinatura")


class CorreiosPostagemPlp(models.Model):
    _name = 'delivery.correios.postagem.plp'

    name = fields.Char(string=u"Descrição", size=20, required=True)
    company_id = fields.Many2one("res.company", string="Empresa")
    state = fields.Selection([('draft', 'Rascunho'), ('done', 'Enviado')],
                             string="Status", default='draft')
    delivery_id = fields.Many2one('delivery.carrier', string=u"Método entrega")
    total_value = fields.Float(string=u"Valor Total")
    sent_date = fields.Date(string="Data Envio")
    carrier_tracking_ref = fields.Char(string="Referência", size=30)
    postagem_ids = fields.One2many('delivery.correios.postagem.objeto',
                                   'plp_id', string=u'Postagens')

    def barcode_url(self):
        url = '<img style="width:125px;height:40px;"\
src="/report/barcode/Code128/' + self.carrier_tracking_ref + '" />'
        return url

    @api.model
    def _get_post_services(self):
        services = {}
        for item in self.postagem_ids:
            serv = item.delivery_id.service_id

            if serv.id not in services:
                services[serv.id] = {}
                services[serv.id]['name'] = serv.name
                services[serv.id]['code'] = serv.code
                services[serv.id]['quantity'] = 0

            services[serv.id]['quantity'] += 1
        return services

    def action_generate_voucher(self):
        self.state = 'done'


class CorreiosPostagemObjeto(models.Model):
    _name = 'delivery.correios.postagem.objeto'

    name = fields.Char(string="Descrição", size=20, required=True)
    delivery_id = fields.Many2one('delivery.carrier', string=u"Método entrega")
    stock_pack_id = fields.Many2one(
        'stock.pack.operation', string="Item Entrega")
    plp_id = fields.Many2one('delivery.correios.postagem.plp', 'PLP')
    evento_ids = fields.One2many(
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

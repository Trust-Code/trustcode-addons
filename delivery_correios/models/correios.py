# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import logging
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from pysigep.sigep import fecha_plp_servicos
except ImportError:
    _logger.debug('Cannot import pysigepweb')


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

    @api.multi
    def unlink(self):
        for item in self:
            if item.state == 'done':
                raise UserError(u'Não é possível excluir uma PLP já enviada')
        return super(CorreiosPostagemPlp, self).unlink()

    def barcode_url(self):
        url = '<img style="width:350px;height:40px;"\
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
        dados = {
            'idPlpCliente': self.id,
            'usuario': self.delivery_id.correio_login,
            'senha': self.delivery_id.correio_password,
            'cartaoPostagem': self.delivery_id.cartao_postagem,
            'numero_contrato': self.delivery_id.num_contrato,
            'numero_diretoria': '36',
            'codigo_administrativo': self.delivery_id.cod_administrativo,
            'nome_remetente': self.company_id.legal_name,
            'logradouro_remetente': self.company_id.street,
            'numero_remetente': self.company_id.number,
            'complemento_remetente': self.company_id.street2,
            'bairro_remetente': self.company_id.district,
            'cep_remetente': re.sub('[^0-9]', '', self.company_id.zip or ''),
            'cidade_remetente': self.company_id.city_id.name,
            'uf_remetente': self.company_id.state_id.code,
            'telefone_remetente': re.sub(
                '[^0-9]', '', self.company_id.phone or ''),
            'email_remetente': self.company_id.email,
        }
        postagens = []
        etiquetas = []
        for item in self.postagem_ids:
            etiqueta = item.name[:10] + item.name[11:]
            etiquetas.append(etiqueta)
            partner = item.stock_pack_id.picking_id.partner_id
            product = item.stock_pack_id.product_id
            postagens.append({
                'numero_etiqueta': etiqueta,
                'codigo_servico_postagem': item.delivery_id.service_id.code,
                'cubagem': '0,0000',
                'peso': "%d" % (product.weight * 1000),
                'nome_destinatario': partner.legal_name or partner.name,
                'telefone_destinatario': re.sub(
                    '[^0-9]', '', partner.phone or ''),
                'celular_destinatario': re.sub(
                    '[^0-9]', '', partner.mobile or ''),
                'email_destinatario': partner.email,
                'logradouro_destinatario': partner.street,
                'complemento_destinatario': partner.street2,
                'numero_end_destinatario': partner.number,
                'bairro_destinatario': partner.district,
                'cidade_destinatario': partner.city_id.name,
                'uf_destinatario': partner.state_id.code,
                'cep_destinatario': re.sub('[^0-9]', '', partner.zip or ''),
                'descricao_objeto': item.stock_pack_id.product_id.name,
                'valor_a_cobrar': '0',
                'valor_declarado': '0',
                'tipo_objeto': '',
                'dimensao_altura': "%d" % product.altura,
                'dimensao_largura': "%d" % product.largura,
                'dimensao_comprimento': "%d" % product.comprimento,
                'dimensao_diametro': "%d" % product.diametro,
                'servicos_adicionais': [
                    '019', '001'
                ]
            })

        dados["objetos"] = postagens
        dados["listaEtiquetas"] = etiquetas
        dados['ambiente'] = self.delivery_id.ambiente
        track_ref = fecha_plp_servicos(**dados)
        if "mensagem_erro" in track_ref:
            raise UserError(track_ref["mensagem_erro"])
        self.write({
            'sent_date': datetime.now(),
            'state': 'done',
            'carrier_tracking_ref': track_ref,
        })


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

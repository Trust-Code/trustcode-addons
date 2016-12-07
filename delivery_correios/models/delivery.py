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
    from pysigep.correios import calcular_preco_prazo, get_eventos
    from pysigep.sigep import busca_cliente, solicita_etiquetas
except ImportError:
    _logger.debug('Cannot import pysigepweb')


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    correio_login = fields.Char(string="Login Correios", size=30)
    correio_password = fields.Char(string="Senha do Correio", size=30)
    cod_administrativo = fields.Char(string="Código Administrativo", size=20)
    num_contrato = fields.Char(string="Número de Contrato", size=20)
    cartao_postagem = fields.Char(
        string="Número do cartão de Postagem", size=20)

    delivery_type = fields.Selection(
        selection_add=[('correios', 'Correios')])
    service_id = fields.Many2one('delivery.correios.service', string="Serviço")
    mao_propria = fields.Selection([('S', 'Sim'), ('N', 'Não')],
                                   string='Entregar em Mão Própria')
    valor_declarado = fields.Boolean('Valor Declarado')
    aviso_recebimento = fields.Selection([('S', 'Sim'), ('N', 'Não')],
                                         string='Receber Aviso de Entrega')

    @api.one
    def action_get_correio_services(self):
        usuario = {
            'idContrato': self.num_contrato,
            'idCartaoPostagem': self.cartao_postagem,
            'usuario': self.correio_login,
            'senha': self.correio_password,
        }
        cliente = busca_cliente(**usuario)
        servicos = cliente.contratos.cartoesPostagem.servicos
        ano_assinatura = cliente.contratos.dataVigenciaInicio
        for item in servicos:
            correio = self.env['delivery.correios.service']
            item_correio = correio.search([('code', '=', item.codigo)])
            if item_correio:
                item_correio.write({
                    'name': item.descricao,
                    'chancela': item.servicoSigep.chancela.chancela,
                    'ano_assinatura': str(ano_assinatura)[:4],
                })
            else:
                correio.create({
                    'code': item.codigo,
                    'identifier': item.id,
                    'chancela': item.servicoSigep.chancela.chancela,
                    'name': item.descricao,
                    'delivery_id': self.id,
                })

    def correios_get_shipping_price_from_so(self, orders):
        ''' For every sale order, compute the price of the shipment

        :param orders: A recordset of sale orders
        :return list: A list of floats, containing the estimated price for the
         shipping of the sale order
        '''
        if len(orders.order_line) == 0:
            raise UserError(u'Não existe nenhum item para calcular')
        custos = []
        for order in orders:
            custo = 0.0
            if not self.service_id:
                raise UserError(u'Escolha o tipo de serviço para poder \
                                calcular corretamente o frete dos correios')

            usuario = {
                'nCdEmpresa': self.cod_administrativo,
                'sDsSenha': self.correio_password,
                'nCdServico': self.service_id.code,
                'sCepOrigem': order.warehouse_id.partner_id.zip,
                'sCepDestino': order.partner_id.zip,
            }

            for line in order.order_line:
                produto = line.product_id
                usuario['nVlPeso'] = produto.weight
                usuario['nCdFormato'] = 1
                usuario['nVlComprimento'] = produto.comprimento
                usuario['nVlAltura'] = produto.altura
                usuario['nVlLargura'] = produto.largura
                usuario['nVlDiametro'] = produto.largura
                usuario['sCdMaoPropria'] = self.mao_propria or 'N'
                usuario['nVlValorDeclarado'] = line.price_subtotal \
                    if self.valor_declarado else 0
                usuario['sCdAvisoRecebimento'] = self.aviso_recebimento or 'N'
                solicita = solicita_etiquetas(**usuario)
                if int(solicita.cServico.Erro) != 0:
                    raise UserError(solicita.cServico.Erro)
                valor = str(solicita.cServico.Valor).replace(',', '.')
                custo = float(valor)
                custos.append(custo)

        return custos

    def correios_send_shipping(self, pickings):
        ''' Send the package to the service provider

        :param pickings: A recordset of pickings
        :return list: A list of dictionaries (one per picking) containing of
                    the form::
                         { 'exact_price': price,
                           'tracking_number': number }
        '''
        solicitacao = {
            'usuario': self.correio_login,
            'senha': self.correio_password,
            'identificador': re.sub(
                '[^0-9]', '', self.company_id.cnpj_cpf or ''),
            'idServico': self.service_id.identifier,
            'qtdEtiquetas': 1
        }
        plp = self.env['delivery.correios.postagem.plp'].search(
            [('state', '=', 'draft')], limit=1)
        if not len(plp):
            name = "%s - %s" % (self.name, datetime.now().strftime("%d-%m-%Y"))
            plp = self.env['delivery.correios.postagem.plp'].create({
                'name': name, 'state': 'draft',
                'delivery_id': self.id, 'total_value': 0,
                'company_id': self.company_id.id,
            })
        res = []
        for picking in pickings:
            tags = []
            preco_soma = 0
            for pack in picking.pack_operation_product_ids:
                usuario_preco_prazo = {
                    'nCdEmpresa': self.cod_administrativo,
                    'sDsSenha': self.correio_password,
                    'nCdServico': self.service_id.code,
                    'sCepOrigem': pack.location_id.company_id.zip,
                    'sCepDestino': picking.partner_id.zip,
                    'nVlPeso': pack.product_id.weight,
                    'nVlComprimento': pack.product_id.comprimento,
                    'nVlAltura': pack.product_id.altura,
                    'nVlLargura': pack.product_id.largura,
                    'nVlDiametro': pack.product_id.diametro,
                    'nCdFormato': 1,
                    'sCdMaoPropria': self.mao_propria,
                    'nVlValorDeclarado': self.product_id.lst_price,
                    'sCdAvisoRecebimento': self.aviso_recebimento,
                }
                preco = calcular_preco_prazo(**usuario_preco_prazo)
                preco = str(preco.cServico.Valor).replace(',', '.')
                preco = float(preco)
                preco_soma += preco * pack.product_qty
                plp.total_value += preco_soma
                etiqueta = solicita_etiquetas(**solicitacao)[0]
                pack.track_ref = etiqueta
                tags.append(etiqueta)
                self.env['delivery.correios.postagem.objeto'].create({
                    'name': etiqueta, 'stock_pack_id': picking.id,
                    'plp_id': plp.id, 'delivery_id': self.id,
                    'company_id': self.company_id.id,
                })
            tags = ';'.join(tags)
            pickings.carrier_tracking_ref = tags
            res.append({'exact_price': preco_soma, 'tracking_number': tags})
        return res

    def correios_get_tracking_link(self, pickings):
        ''' Ask the tracking link to the service provider

        :param pickings: A recordset of pickings
        :return list: A list of string URLs, containing the tracking links
         for every picking
        '''
        usuario = {
            'usuario': self.correio_login,
            'senha': self.correio_password,
        }
#       tracking_refs = ['PL207893158BR', 'JS535334467BR']
        for picking in pickings:
            for pack in picking.pack_operation_product_ids:
                track_ref = list(pack.track_ref)
                usuario['objetos'] = track_ref
                objetos = get_eventos(**usuario).objeto
                for objeto in objetos:
                    postagem = self.env['delivery.correios.postagem.objeto'].\
                        search([('stock_pack_id', '=', pack.id)], limit=1)
                    correio_evento = {
                        'etiqueta': objeto.numero,
                        'postagem_id': postagem.id
                    }
                    for evento in objeto.get('evento', []):
                        correio_evento['status'] = evento.status
                        correio_evento['data'] = datetime.strptime(
                            str(evento.data), '%d/%m/%Y')
                        correio_evento['local_origem'] = evento.local +\
                            ' - ' + str(evento.codigo) + ', ' +\
                            evento.cidade + '/' + evento.uf
                        correio_evento['descricao'] = evento.descricao
                        if 'destino' in evento:
                            correio_evento['local_destino'] =\
                                evento.destino.local + ' - ' +\
                                str(evento.destino.codigo) + ', ' +\
                                evento.destino.cidade + '/' + evento.destino.uf
                    self.env['delivery.correios.postagem.eventos'].create(
                        correio_evento)
        return ['/web#min=1&limit=80&view_type=list&model=delivery.correios.postagem.plp&action=396']


    def correios_cancel_shipment(self):
        ''' Cancel a shipment

        :param pickings: A recordset of pickings
        '''
        pass

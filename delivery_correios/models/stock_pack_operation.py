# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    from pysigep.correios import sign_chancela
except ImportError:
    _logger.debug('Cannot import pysigepweb')


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "Qtd: %s - %s" % (
                rec.product_qty, rec.product_id.name)))
        return result

    track_ref = fields.Char(string="Etiqueta de Rastreamento")

    def tracking_qrcode(self):
        origem = self.picking_id.company_id
        destino = self.picking_id.partner_id

        dados = {}

        dados['destino_cep'] = re.sub('[^0-9]', '', destino.zip or '')
        dados['destino_compl'] = re.sub(r'\D', '', destino.number or '').\
            zfill(5)
        dados['origem_cep'] = re.sub('[^0-9]', '', origem.zip or '')
        dados['origem_compl'] = re.sub(r'\D', '', origem.number or '')\
            .zfill(5)
        validador_cep_dest = sum([int(n) for n in re.sub(r'\D', '',
                                                         destino.zip) or ''])
        next_10 = validador_cep_dest
        while next_10 % 10 != 0:
            next_10 += 1
        dados['validador_cep_dest'] = next_10 - validador_cep_dest

        dados['idv'] = '51'

        dados['etiqueta'] = self.track_ref

        transportadora = self.picking_id.carrier_id
        servicos_adicionais = ''
        servicos_adicionais += '01' if transportadora.aviso_recebimento == 'S'\
            else '00'
        servicos_adicionais += '02' if transportadora.mao_propria == 'S'\
            else '00'
        servicos_adicionais += '19' if transportadora.valor_declarado else '00'
        dados['servicos_adicionais'] = servicos_adicionais.ljust(12, '0')

        dados['cartao_postagem'] = transportadora.cartao_postagem.zfill(10)
        dados['codigo_servico'] = transportadora.service_id.code
        dados['agrupamento'] = '00'
        dados['num_logradouro'] = destino.number.zfill(5) or '0' * 5
        dados['compl_logradouro'] = '{:.20}'.format(str(destino.street2))\
            .zfill(20)
        dados['valor_declarado'] = str(self.product_id * self.product_qty).\
            replace('.', '').replace(',', '').zfill(5)\
            if transportadora.valor_declarado else '00000'
        if destino.phone:
            telefone = re.sub(r'\D', '', destino.phone).replace(' ', '')\
                .zfill(12)
        elif destino.mobile:
            telefone = re.sub(r'\D', '', destino.mobile).replace(' ', '')\
                .zfill(12)
        else:
            telefone = '0' * 12
        dados['telefone'] = telefone
        dados['latitude'] = '-00.000000'
        dados['longitude'] = '-00.000000'
        dados['pipe'] = '|'
        dados['reserva'] = ' ' * 30
        code = '{destino_cep}{destino_compl}{origem_cep}{origem_compl}\
{validador_cep_dest}{idv}{etiqueta}{servicos_adicionais}{cartao_postagem}\
{codigo_servico}{agrupamento}{num_logradouro}{compl_logradouro}\
{valor_declarado}{telefone}{latitude}{longitude}{pipe}{reserva}'.\
            format(**dados)

        url = '<img style="width:125px;height:125px;"\
src="/report/barcode/QR/' + code + '" />'
        return url

    def tracking_barcode(self):
        url = '<img style="width:350px;height:70px;"\
src="/report/barcode/Code128/' + self.track_ref + '" />'
        return url

    def zip_dest_barcode(self):
        cep = re.sub('[^0-9]', '', self.picking_id.partner_id.zip or '')
        url = '<img style="width:200px;height:50px;"\
src="/report/barcode/Code128/' + cep + '" />'
        return url

    def get_chancela(self):

        picking = self.picking_id
        transportadora = picking.carrier_id

        nome = picking.company_id.legal_name
        ano_assinatura = transportadora.service_id.ano_assinatura
        contrato = transportadora.num_contrato
        origem = self.location_id.company_id.state_id.code
        postagem = picking.partner_id.state_id.code
        usuario_correios = {
            'contrato': contrato, 'nome': nome,
            'ano_assinatura': ano_assinatura,
            'origem': origem, 'postagem': postagem,
        }

        chancela = self.with_context({'bin_size': False}).\
            picking_id.carrier_id.service_id.chancela

        chancela = sign_chancela(chancela, usuario_correios)

        return '<img style="height: 114px; width: 114px"\
src="data:image/png;base64,' + chancela + '"/>'

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
        origem = re.sub('[^0-9]', '', self.picking_id.company_id.zip or '')
        destino = re.sub('[^0-9]', '', self.picking_id.partner_id.zip or '')

        # TODO Implementar o código correto aqui.
        code = '%s00000%s00000' % (destino, origem)

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

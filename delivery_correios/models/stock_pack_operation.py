# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

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

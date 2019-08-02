# © 2019 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging
from io import BytesIO

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    from openpyxl import load_workbook
except ImportError:
    _logger.error('Cannot import openpyxl', exc_info=True)


# class StockPackOperationLot(models.Model):
#     _inherit = 'stock.pack.operation.lot'
#
#     @api.model
#     def create(self, vals):
#        if "lot_name" in vals and "operation_id" in vals and vals['lot_name']:
#            op = self.env['stock.pack.operation'].browse(vals['operation_id'])
#             total = self.search_count(
#                 [('lot_name', '=', vals['lot_name']),
#                  ('operation_id', '=', op.id)])
#             if total > 0:
#                 raise UserError(
#                  u'Você já mencionou este nome de lote em outra linha: %s' %
#                     vals['lot_name'])
#         return super(StockPackOperationLot, self).create(vals)


class StockMove(models.Model):
    _inherit = 'stock.move'

    serials_xlsx = fields.Binary(string="XLS de Lotes")

    @api.onchange('serials_xlsx')
    def _onchange_serials_xlsx(self):
        if not self.serials_xlsx:
            return
        xlsx = base64.b64decode(self.serials_xlsx.encode('utf-8'))
        xlsx = BytesIO(xlsx)
        wb = load_workbook(filename=xlsx)
        lot_names = []
        for sheet in wb.worksheets:
            for row in sheet.rows:
                if len(row) < 2:
                    continue
                for x in range(1, len(row), 3):
                    if row[x].value:
                        lot_names.append(row[x].value)

        self.serials_xlsx = None
        for lote in lot_names:
            line_id = self.move_line_ids.filtered(
                lambda x: x.lot_id.name == lote or x.lot_name == lote)
            if line_id:
                line_id.qty_done += 1
            else:
                line_id = self.move_line_ids.filtered(
                    lambda x: not x.lot_name and not x.lot_id)
                if line_id:
                    lot_id = self.env['stock.production.lot'].search(
                        [('name', '=', lote),
                         ('product_id', '=', self.product_id.id)])
                    line_id[0].update({'lot_name': lote, 'qty_done': 1,
                                       'lot_id': lot_id.id})

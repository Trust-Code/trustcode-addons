# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)

        info = ''
        for move in self.procurement_ids.move_ids:
            # Verifica a entrega mais recente finalizada e adiciona os lotes
            if move.state == 'done':
                for lote in move.lot_ids:
                    date = fields.Datetime.from_string(lote.life_date)
                    info += u"Lote/Série: %s" % lote.name
                    if date:
                        info += "/ Vencimento: %s" % date.strftime("%d/%m/%Y")
                    info += "\n"
                break
        res['informacao_adicional'] = info
        return res

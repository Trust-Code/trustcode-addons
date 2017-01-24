# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class SaleContractRenew(models.TransientModel):
    _name = 'sale.contract.renew'

    addition_discount = fields.Float(
        string="% Acréscimo/Desc.",
        help="Adicione um valor negativo para desconto")

    @api.multi
    def action_update_contracts(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        for order in sale_orders:
            end_date = fields.Date.from_string(order.end_contract)
            order.end_contract = end_date + relativedelta(years=1)

            for line in order.order_line:
                percentual = 1.0 + (self.addition_discount / 100)
                line.price_unit = round(line.price_unit * percentual, 2)

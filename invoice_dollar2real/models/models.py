# -*- coding: utf-8 -*-
# © 2017 Felipe Paloschi <paloschi.eca@gmail.com>, Trustcode
# © 2017 Johny Chen Jy <johnychenjy@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _prepare_invoice(self):
        currency = self.env['res.currency'].search([('name', '=', 'BRL')])
        inv = super(SaleOrder, self)._prepare_invoice()
        inv['currency_id'] = currency.id
        return inv


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_invoice_line(self, qty):
        currency = self.env['res.currency'].search([('name', '=', 'BRL')])
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if currency.id != self.order_id.pricelist_id.currency_id.id:
            res['price_unit'] = res['price_unit'] *\
                currency.rate / self.order_id.pricelist_id.currency_id.rate
        return res

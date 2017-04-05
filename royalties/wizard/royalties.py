# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from datetime import datetime, date, timedelta


class royalties(models.Model):
    _name = 'royalties.wizard'

    date_to = fields.Date(string=u"Até", required=True)
    date_from = fields.Date(string="De", required=True)
    validity_date = fields.Date(string="Data de Validade")
    royalty_type = fields.Char(string="Tipo")
    product_id = fields.Many2one(
        'product.template', string="Produto")
    commission_ids = fields.One2many(
        'royalties.contract.commission.rule', 'contract_id')
    partner_id = fields.Many2one('res.partner', string=u'Beneficiários')
    region = fields.Char(string=u"Região", size=20)

    def create_commission(self):
        search_vals = []
        search_vals.append(('validity_date', '>=', self.date_from))
        # search_vals.append(('validity_date', '<=', self.date_to))

        contract_ids = self.env['royalties.contract'].search(search_vals)

        for contract_id in contract_ids:
            commission_ids = self.env['royalties.commission.invoiced'].search([
                ('contract_id', '=', contract_id.id)])
            for commission_id in commission_ids:
                invoice_id = self.env['account.invoice'].search([
                    ('id', '=', commission_id.invoice_line_id.invoice_id.id)])
                date = invoice_id.date_invoice
                if not (date >= self.date_from and date <= self.date_to):
                    continue
                if commission_id.voucher_id:
                    continue
                account_id = 0
                prod_id = contract_id.product_id
                part_id = contract_id.partner_id
                categ_id = prod_id.categ_id
                if prod_id.property_account_expense_id:
                    account_id = prod_id.property_account_expense_id
                else:
                    account_id = categ_id.property_account_expense_categ_id


                voucher_type = self.env['account.journal'].search([
                    ('type', '=', 'purchase')])
                voucher = {
                    'account_id': part_id.property_account_payable_id.id,
                    'validity_date': contract_id.validity_date,
                    'pay_now': 'pay_later',
                    'partner_id': part_id.id,
                    'voucher_type': voucher_type.type,
                    'journal_id': voucher_type.id,
                }

                product_price = 0.0
                if part_id.government:
                    product_price = prod_id.standard_price
                else:
                    product_price = prod_id.list_price

                product_id = self.env['product.product'].search([
                    ('product_tmpl_id', '=', prod_id.id)])

                voucher_line = {
                    'account_id': account_id.id,
                    'product_id': product_id.id,
                    'price_unit': commission_id.commission,
                    'quantity': '1',
                    'name': prod_id.description or 'royalties',
                }
                voucher['line_ids'] = [(0, None, voucher_line)]
                voucher_id = self.env['account.voucher'].create(voucher)
                commission_id.voucher_id = voucher_id.id

# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
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
        if self.partner_id:
            search_vals.append(('partner_id', '=', self.partner_id.id))
        if self.product_id:
            search_vals.append(('product_id', '=', self.product_id.id))
        if self.royalty_type:
            search_vals.append(('royalty_type', '=', self.royalty_type))
        if self.region:
            search_vals.append(('region', '=', self.region))
        search_vals.append(('validity_date', '>=', self.date_from))
        search_vals.append(('validity_date', '<=', self.date_to))

        contract_ids = self.env['royalties.contract'].search(search_vals)

        for contract_id in contract_ids:
            commission_id = self.env['royalties.commission.invoiced'].search([
                ('contract_id', '=', contract_id.id)])
            if commission_id.voucher_id:
                import ipdb; ipdb.set_trace()
                continue
            account_id = 0
            prod_id = contract_id.product_id
            part_id = contract_id.partner_id
            if prod_id.property_account_expense_id:
                account_id = prod_id.property_account_expense_id
            else:
                account_id = prod_id.categ_id.property_account_expense_categ_id


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

            voucher_line = {
                'account_id': account_id.id,
                'product_id': prod_id.id,
                'price_unit': commission_id.commission,
                'quantity': '1',
                'name': prod_id.description or 'royalties',
            }
            voucher['line_ids'] = [(0, None, voucher_line)]
            voucher_id = self.env['account.voucher'].create(voucher)
            commission_id.voucher_id = voucher_id.id

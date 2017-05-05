# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            qty_to_invoice = 0.0
            for line in invoice.invoice_line_ids:
                line.commission_total = 0.0
                if not line.product_id.contract_ids:
                    continue
                line.commission_invoiced_ids.unlink()
                for contract in line.product_id.contract_ids:
                    if contract.validity_date < invoice.date_invoice:
                        continue
                    comm_ids = contract.commission_ids.sorted(
                        key=lambda r: r.min_qty, reverse=True)
                    for commission_id in comm_ids:
                        qty_to_invoice = line.quantity
                        if qty_to_invoice >= commission_id.min_qty:
                            product_value = 0.0
                            if contract.partner_id.government:
                                product_value = line.product_id.standard_price
                            else:
                                product_value = line.product_id.list_price
                            comm_perc = (commission_id.commission / 100)
                            qty_sold = (product_value * qty_to_invoice)
                            commission_line = (qty_sold * comm_perc)
                            vals = {
                                'commission': commission_line,
                                'partner_id': contract.partner_id.id,
                                'invoice_line_id': line.id,
                                'contract_id': contract.id,
                            }
                            line.commission_total += commission_line
                            self.env['royalties.commission.invoiced'].create(
                                vals)
        return super(AccountInvoice, self).invoice_validate()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    commission_invoiced_ids = fields.One2many(
        'royalties.commission.invoiced', 'invoice_line_id')
    commission_total = fields.Float(
        string="Commissions")

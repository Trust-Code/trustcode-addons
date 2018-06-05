# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    branch_partner_id = fields.Many2one(comodel_name='res.partner',
                                        string='Filial')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountInvoice, self).finalize_invoice_move_lines(
            move_lines)
        for line in res:
            vals = line[2]
            invoice = self.env['account.invoice'].browse(vals['invoice_id'])
            invoice_line = invoice.invoice_line_ids.search([
                ('invoice_id', '=', invoice.id),
                ('product_id', '=', vals['product_id']),
                ('price_subtotal', 'in', [vals['debit'], vals['credit']]),
                ('name', '=', vals['name'])])
            if line:
                vals.update(
                    {'branch_partner_id': invoice_line.branch_partner_id.id})
        return res

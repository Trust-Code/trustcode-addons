# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountInvoice, self).\
            finalize_invoice_move_lines(move_lines)

        if self.partner_shipping_id.invoiceto_id:
            for invoice_line in res:
                line = invoice_line[2]
                line['partner_id'] = self.partner_shipping_id.id
        return res

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            if invoice.partner_shipping_id.invoiceto_id:
                invoice.message_unsubscribe([invoice.partner_id.id])
                invoice.message_subscribe([invoice.partner_shipping_id.id])
        return res

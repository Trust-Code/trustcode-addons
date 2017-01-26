# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):
        for rec in self:
            if rec.invoice_ids and \
               rec.invoice_ids[0].partner_shipping_id.invoiceto_id:
                rec.partner_id = rec.invoice_ids[0].partner_shipping_id
        super(AccountPayment, self).post()

    def _get_counterpart_move_line_vals(self, invoice=False):
        res = super(AccountPayment, self)._get_counterpart_move_line_vals(
            invoice=invoice)
        if invoice and invoice[0].partner_shipping_id.invoiceto_id:
            res.update({
                'partner_id': invoice[0].partner_shipping_id.id
            })
        return res

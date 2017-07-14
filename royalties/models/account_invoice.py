# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_validate(self):
        self.invoice_line_ids.validate_royalties()
        return super(AccountInvoice, self).invoice_validate()

    @api.multi
    def action_invoice_cancel_paid(self):
        res = super(AccountInvoice, self).action_invoice_cancel_paid()

        if res is True:
            self.env['account.royalties.payment'].search(
                [['inv_line_id', 'in', self.invoice_line_ids.ids]]).unlink()

        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def validate_royalties(self):
        '''
        Essa função busca os contratos de royalties corretos para cada linha da
        fatura. O objetivo é deixar vinculado o contrato ativo no dia em que
        foi faturado para posterior faturamento da comissão.
        '''
        for line in self:
            domain = [('product_id', '=', line.product_id.id),
                      ('royalties_id.state', '=', 'in_progress'), '|',
                      ('royalties_id.company_id', '=',
                      line.invoice_id.company_id.id),
                      ('royalties_id.company_id', '=', False)]
            royalties_line_ids = self.env['royalties.lines'].search(domain)
            if royalties_line_ids:
                line_payment = self.env['account.royalties.payment']
                line_payment.create_line_payment(royalties_line_ids, line)


class AccountRoyaltiesPayment(models.Model):
    _name = "account.royalties.payment"

    inv_line_id = fields.Many2one('account.invoice.line', ondelete='set null')
    product_id = fields.Many2one('product.product', required=True,
                                 string="Product", ondelete='set null')
    royalties_id = fields.Many2one('royalties', required=True,
                                   string='Royalties', ondelete='restrict')
    voucher_id = fields.Many2one('account.voucher', ondelete='set null')

    @api.multi
    def create_line_payment(self, royalties_line_ids, inv_line_id):
        for line in royalties_line_ids:
            vals = {'inv_line_id': inv_line_id.id,
                    'royalties_id': line.royalties_id.id,
                    'product_id': line.product_id.id}
            self.create(vals)

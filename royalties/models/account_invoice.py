# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_validate(self):
        if self.fiscal_position_id.royalties:
            if self.fiscal_position_id.finalidade_emissao == '1':
                self.invoice_line_ids.validate_royalties(False)
            elif self.fiscal_position_id.finalidade_emissao == '4':
                self.invoice_line_ids.validate_royalties(True)

        return super(AccountInvoice, self).invoice_validate()

    @api.multi
    def action_cancel(self):
        import ipdb
        ipdb.set_trace()
        res = super(AccountInvoice, self).action_cancel()

        if res is True:
            self.env['account.royalties.line'].search(
                [['inv_line_id', 'in', self.invoice_line_ids.ids]]).unlink()

        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    account_royalties_line_ids = fields.One2many('account.royalties.line',
                                                 'inv_line_id',
                                                 ondelete='set null')

    @api.multi
    def validate_royalties(self, devol=False):
        '''
        Essa função busca os contratos de royalties corretos para cada linha da
        fatura. O objetivo é deixar vinculado o contrato ativo no dia em que
        foi faturado para posterior faturamento da comissão.
        '''
        for line in self:
            domain = [('state', '=', 'in_progress'), '|',
                      ('company_id', '=', line.invoice_id.company_id.id),
                      ('company_id', '=', False)]
            royalties = self.env['royalties'].search(domain)
            royalties_ids = []
            for r in royalties:
                lines = r.line_ids.filtered(
                    lambda l: l.product_id.id == line.product_id.id)
                if len(lines) > 0:
                    royalties_ids += r
            if royalties_ids:
                line_payment = self.env['account.royalties.line']
                line_payment.create_account_royalties_line(
                    royalties_ids, line, devol)


class AccountRoyaltiesPayment(models.Model):
    _name = "account.royalties.line"

    inv_line_id = fields.Many2one('account.invoice.line', ondelete='set null')
    is_devol = fields.Boolean('Is Devolution')
    product_id = fields.Many2one('product.product', required=True,
                                 string="Product", ondelete='set null')
    royalties_id = fields.Many2one('royalties', required=True,
                                   string='Royalties', ondelete='restrict')
    voucher_id = fields.Many2one('account.voucher', ondelete='set null')
    inv_line_dev_ids = fields.Many2many('account.invoice.line')

    @api.multi
    def create_account_royalties_line(
            self, royalties_ids, inv_line_id, devol=False):
        for r in royalties_ids:
            vals = {'inv_line_id': inv_line_id.id,
                    'royalties_id': r.id,
                    'product_id': inv_line_id.product_id.id,
                    'is_devol': devol}
            self.create(vals)

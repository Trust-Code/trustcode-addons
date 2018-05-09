# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency,
                                 current_currency):
        res = super(AccountVoucher, self).voucher_move_line_create(
            line_total, move_id, company_currency, current_currency)
        move = self.env['account.move'].browse(move_id)
        for line in self.line_ids:
            move_line = move.line_ids.search([
                ('name', '=', line.name),
                ('account_id', '=', line.account_id.id),
                ('quantity', '=', line.quantity),
                ('analytic_account_id', '=', line.account_analytic_id.id)],
                limit=1)
            if move_line:
                move_line.update({'branch_partner_id': line.branch_partner_id})
        return res


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    branch_partner_id = fields.Many2one('res.partner', 'Filial')

    @api.onchange('branch_partner_id')
    def _onchange_branch_partner_id(self):
        if self.branch_partner_id:
            return {'domain': {'account_analytic_id': [(
                'partner_id', '=', self.branch_partner_id.id)]}}
        else:
            return {'domain': {'account_analytic_id': []}}

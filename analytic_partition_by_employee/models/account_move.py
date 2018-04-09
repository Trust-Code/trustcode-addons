# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    branch_partner_id = fields.Many2one('res.partner', 'Filial')

    def _create_partition_move_lines(self, partition_group):
        if self.branch_partner_id and self.analytic_account_id:
            return
        elif self.branch_partner_id:
            analytic_account = self.env['account.analytic.account'].search([
                ('partner_id', '=', self.branch_partner_id.id),
                ('partition_id', '!=', False)], limit=1)
            self.analytic_account_id = analytic_account
            partition_group = analytic_account.partition_id
        return super(AccountMoveLine, self)._create_partition_move_lines(
            partition_group)

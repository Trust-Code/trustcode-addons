# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        for line in self.line_ids:
            line._create_partition_move_lines(
                line.analytic_account_id.partition_id)
        return super(AccountMove, self).post()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def update_partition_move_line(self, credit, debit,
                                   app_line=False):
        if app_line:
            percent = app_line.partition_percent
            self.update({
                'analytic_account_id': app_line.analytic_account_id
            })
        else:
            percent = 100
        self.with_context(check_move_validity=False).update({
            'credit': (credit * percent / 100),
            'debit': (debit * percent / 100),
            })
        return self.credit, self.debit

    def _create_partition_move_lines(self, partition_group):
        if not partition_group:
            return
        initial_credit = credit = self.credit
        initial_debit = debit = self.debit
        move_lines = []
        for app_line in partition_group.partition_line_ids:
            move_line = self.with_context(check_move_validity=False).copy()
            new_credit, new_debit = move_line.update_partition_move_line(
                initial_credit, initial_debit, app_line)
            credit -= new_credit
            debit -= new_debit
            move_lines.append(move_line)
        self.update_partition_move_line(credit, debit)
        move_lines.append(self)
        return move_lines

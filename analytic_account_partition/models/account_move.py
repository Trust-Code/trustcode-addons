# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        for line in self.line_ids:
            partition = line.account_id.partition_id or\
                line.analytic_account_id.partition_id
            if not partition.operation_type:
                line._create_partition_move_lines(
                    partition_group=partition)
            elif partition.operation_type == 'out' and\
                    line.move_id.journal_id.type == 'sale':
                line._create_partition_move_lines(
                    partition_group=partition)
            elif partition.operation_type == 'in' and\
                    line.move_id.journal_id.type == 'purchase':
                line._create_partition_move_lines(
                    partition_group=partition)
        return super(AccountMove, self).post()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _create_partition_move_lines(self, partition_group):
        if not partition_group:
            return
        initial_credit = sum_credit = self.credit
        initial_debit = sum_debit = self.debit
        move_lines = []
        for app_line in partition_group.partition_line_ids:
            move_line = self.with_context(check_move_validity=False).copy()
            new_credit, new_debit = move_line.update_partition_move_line(
                initial_credit, initial_debit, app_line)
            credit = sum_credit - new_credit
            debit = sum_debit - new_debit
            if credit < 0 or debit < 0:
                new_credit, new_debit = move_line.update_partition_move_line(
                    credit=move_line.credit + credit,
                    debit=move_line.debit + debit
                )
            sum_credit -= round(new_credit, 2)
            sum_debit -= round(new_debit, 2)
            move_lines.append(move_line)
        self.update_partition_move_line(sum_credit, sum_debit)
        move_lines.append(self)
        return move_lines

    def update_partition_move_line(self, credit, debit,
                                   app_line=False):
        if app_line:
            percent = app_line.partition_percent
            self.write({
                'analytic_account_id': app_line.analytic_account_id.id
            })
        else:
            percent = 100
        self.with_context(check_move_validity=False).write({
            'credit': (credit * percent / 100),
            'debit': (debit * percent / 100),
            })
        return self.credit, self.debit

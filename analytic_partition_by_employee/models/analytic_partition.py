# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AnalyticPartition(models.Model):
    _inherit = 'analytic.partition'

    def get_employee_per_account(self, id):
        employee_parts = self.env['hr.employee.partition'].search([
            ('employee_id.active', '=', True),
            ('analytic_account_id', '=', id)
        ])
        return sum(part.weight / len(part.employee_id.employee_partition_ids)
                   for part in employee_parts)

    def calc_percent_by_employee(self):
        analytic_accs = self.env['account.analytic.account'].search(
            [('partition_id', '=', self.id)], limit=1)
        analytic_accs |= self.partition_line_ids.mapped('analytic_account_id')
        accounts = analytic_accs.filtered(lambda x: x.active)
        total_employee = sum(
            [self.get_employee_per_account(acc.id)
             for acc in accounts])
        if not self.partition_line_ids:
            return
        for line in self.partition_line_ids:
            if not line.analytic_account_id.active:
                line.partition_percent = 0
                continue
            line.partition_percent = (self.get_employee_per_account(
                line.analytic_account_id.id)
                / total_employee * 100) if total_employee else 0

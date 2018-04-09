# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class Analyticpartition(models.Model):
    _inherit = 'analytic.partition'

    def get_employee_per_account(self, id):
        employees = self.env['hr.employee'].search([
            ('active', '=', True)]).filtered(
            lambda x: id in x.analytic_account_ids.ids)
        return sum(1/len(employee.analytic_account_ids)
                   for employee in employees)

    def calc_percent_by_employee(self):
        total_employee = sum(
            [self.get_employee_per_account(line.analytic_account_id.id)
             for line in self.partition_line_ids])
        amount = 0
        balance_line = False
        for line in self.partition_line_ids:
            if not line.is_account_active:
                line.partition_percent = 0
                continue
            if not balance_line:
                balance_line = line
                continue
            line.partition_percent = (self.get_employee_per_account(
                line.analytic_account_id.id)/total_employee * 100) if\
                total_employee else 0
            amount += line.partition_percent
            line.type = 'percent'
        balance_line.type = 'balance'
        balance_line.partition_percent = 100 - amount

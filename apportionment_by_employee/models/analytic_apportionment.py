# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AnalyticApportionment(models.Model):
    _inherit = 'analytic.apportionment'

    def get_employee_per_account(self, id):
        employees = self.env['hr.employee'].search([]).filtered(
            lambda x: id in x.analytic_account_ids.ids)
        return sum(1/len(employee.analytic_account_ids)
                   for employee in employees)

    def calc_percent_by_employee(self):
        total_employee = sum(
            [self.get_employee_per_account(line.analytic_account_id.id)
             for line in self.apportionment_line_ids])
        amount = 0
        for line in self.apportionment_line_ids[:-1]:
            line.apportionment_percent = self.get_employee_per_account(
                line.analytic_account_id.id)/total_employee * 100
            amount += line.apportionment_percent
            line.type = 'percent'
        self.apportionment_line_ids[-1].type = 'balance'
        self.apportionment_line_ids[-1].apportionment_percent = 100 - amount

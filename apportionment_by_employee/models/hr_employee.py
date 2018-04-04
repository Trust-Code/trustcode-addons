# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    analytic_account_ids = fields.Many2many(
        'account.analytic.account', string='Conta Analitica')

    def compute_percent_per_employe(self):
        apportionment_groups = set(
            [acc.apportionment_id for acc in self.analytic_account_ids])
        for app in apportionment_groups:
            app.calc_percent_by_employee()

    @api.multi
    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        if vals.get('analytic_account_ids'):
            self.compute_percent_per_employe()
        return res

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        res.compute_percent_per_employe()
        return res

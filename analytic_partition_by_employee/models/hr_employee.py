# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    analytic_account_ids = fields.Many2many(
        'account.analytic.account', string='Conta Analitica')

    def compute_percent_per_employe(self):
        partition_groups = []
        for acc in self.analytic_account_ids:
            if acc.partition_id:
                partition_groups.append(acc.partition_id)
            else:
                part_group = self.env['account.analytic.account'].search([
                    ('partner_id', '=', acc.partner_id.id),
                    ('partition_id', '!=', False)], limit=1).mapped(
                        'partition_id')
                partition_groups.append(part_group)
        for app in partition_groups:
            app.calc_percent_by_employee()

    @api.multi
    def write(self, vals):
        res = super(Employee, self).write(vals)
        if vals.get('analytic_account_ids') or vals.get('active'):
            self.compute_percent_per_employe()
        return res

    @api.model
    def create(self, vals):
        res = super(Employee, self).create(vals)
        res.compute_percent_per_employe()
        return res

# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_branch = fields.Boolean('É Filial')
    department_ids = fields.Many2many(
        'hr.department', string="Departamentos")

    def create_partition_group(self, analytic_acc):
        part_group = self.env['analytic.partition'].create({
            'name': 'Rateio ' + self.name,
        })
        analytic_acc.partition_id = part_group
        return part_group

    def create_partition_lines(self, partition_id, analytic_accounts):
        accounts = []
        accounts_in_group = partition_id.partition_line_ids.mapped(
            'analytic_account_id')
        for acc in analytic_accounts:
            if acc in accounts_in_group:
                continue
            accounts.append(self.env['analytic.partition.line'].create({
                'partition_id': partition_id.id,
                'analytic_account_id': acc.id,
                'partition_percent': 0,
            }))
        return accounts

    def deactivate_analytic_account(self, departments):
        for dep in departments:
            analytic_acc = self.env['account.analytic.account'].search([
                ('partner_id', '=', self.id),
                ('department_id', '=', dep.id)
            ], limit=1)
            if analytic_acc and analytic_acc.active:
                analytic_acc.toggle_active()

                if analytic_acc.partition_id:
                    self.change_partition_account(analytic_acc)

    def change_partition_account(self, analytic_acc):
        partition_id = analytic_acc.partition_id
        if not any(item.analytic_account_id.active for item in
                   partition_id.partition_line_ids):
            partition_id.unlink()
            return
        analytic_acc.write({
            'partition_id': False
        })
        self.create_partition_lines(partition_id, analytic_acc)
        for line in partition_id.partition_line_ids:
            if line.analytic_account_id.active:
                line.analytic_account_id.partition_id = partition_id
                line.unlink()
                break

    def create_analytic_accounts(self, departments):
        analytic_accs = []
        for dep in departments:
            analytic_acc = self.env['account.analytic.account'].search([
                ('partner_id', '=', self.id),
                ('department_id', '=', dep.id),
                ('active', '=', False)
            ])
            if analytic_acc and not analytic_acc.active:
                analytic_acc.toggle_active()
            else:
                analytic_acc = self.env['account.analytic.account'].create({
                    'name': dep.name,
                    'partner_id': self.id,
                    'department_id': dep.id,
                })
            analytic_accs.append(analytic_acc)
        part_group = self.env['account.analytic.account'].search([
            ('partner_id', '=', self.id),
            ('partition_id', '!=', False),
            '|',
            ('active', '=', False),
            ('active', '=', True)], limit=1).partition_id
        if not part_group:
            part_group = self.create_partition_group(analytic_accs[0])
            analytic_accs = analytic_accs[1:]
        self.create_partition_lines(part_group, analytic_accs)
        matrix_partition = self.env.ref(
            "analytic_partition_by_employee.matrix_partition_group")
        self.create_partition_lines(matrix_partition, analytic_accs)
        return analytic_accs

    def _update_analytic_accounts(self, departments):
        departments_to_remove = [item for item in self.department_ids]
        departments_to_create = [item for item in departments]
        for item in self.department_ids:
            for dep in departments:
                if item == dep:
                    departments_to_remove.remove(item)
                    departments_to_create.remove(dep)
                    break
        if departments_to_create:
            self.create_analytic_accounts(departments_to_create)
        if departments_to_remove:
            self.deactivate_analytic_account(departments_to_remove)

    def _check_analytic_accounts(self, vals):
        departments = self.env['hr.department'].browse(
            vals['department_ids'][0][2])
        if sorted(departments) != sorted(self.department_ids):
            self._update_analytic_accounts(departments)
        part_group = self.env['account.analytic.account'].search([
            ('department_id', 'in', self.department_ids.ids),
            ('partner_id', '=', self.id),
            ('partition_id', '!=', False)], limit=1).partition_id
        self.env.ref("analytic_partition_by_employee.matrix_partition_group").\
            sudo().calc_percent_by_employee()
        part_group.calc_percent_by_employee()

    @api.multi
    def write(self, vals):
        if vals.get('department_ids'):
            self._check_analytic_accounts(vals)
        res = super(ResPartner, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if vals.get('department_ids') and res.is_branch:
            departments = self.env['hr.department'].browse(
                vals['department_ids'][0][2])
            if departments:
                res.create_analytic_accounts(departments)
        return res

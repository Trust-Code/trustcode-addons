# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_branch = fields.Boolean('É Filial')
    expense_group_ids = fields.Many2many(
        'expense.group', string="Grupo de contas")
    # count_partition_lines = fields.Integer(
    #     'Linhas de Rateio',
    #     compute="_compute_partition_lines")

    # @api.multi
    # def _compute_partition_lines(self):
    #     for item in self:
    #         app_groups = set(map(lambda x: x.partition_id, self.env[
    #             'account.analytic.account'].search(
    #                 [('partner_id', '=', item.id)])))
    #         item.count_partition_lines = sum(
    #             [len(app.partition_line_ids) for app in app_groups])

    def create_partition_group(self, analytic_accs):
        part_group = self.env['analytic.partition'].create({
            'name': 'Escritório ' + self.name,
            'partition_line_ids': [(0, 0, {
                'analytic_account_id': acc.id,
                'partition_percent': 0
            }) for acc in analytic_accs[1:]]
        })
        analytic_accs[0].update({
            'partition_id': part_group.id,
        })
        return part_group

    def create_partition_line(self, partition_id, analytic_acc):
        return self.env['analytic.partition.line'].create({
            'partition_id': partition_id.id,
            'analytic_account_id': analytic_acc.id,
            'partition_percent': 0,
        })

    def deactivate_analytic_account(self, groups):
        for group in groups:
            analytic_acc = self.env['account.analytic.account'].search([
                ('partner_id', '=', self.id),
                ('expense_group_id', '=', group.id)
            ])
            if analytic_acc and analytic_acc.active:
                analytic_acc.toggle_active()

                if analytic_acc.partition_id:
                    partition_id = analytic_acc.partition_id
                    if not any(item.isactive for item in
                               partition_id.partition_line_ids):
                        return
                    analytic_acc.update({
                        'partition_id': False
                    })
                    self.create_partition_line(partition_id, analytic_acc)
                    for line in partition_id.partition_line_ids:
                        if line.analytic_account_id.active:
                            line.analytic_account_id.partition_id =\
                                partition_id
                            line.unlink()
                            return

    def create_analytic_account(self, groups, create_group=False):
        analytic_accs = []
        for group in groups:
            analytic_acc = self.env['account.analytic.account'].search([
                ('partner_id', '=', self.id),
                ('expense_group_id', '=', group.id),
                ('active', '=', False)
            ])
            if analytic_acc and not analytic_acc.active:
                analytic_acc.toggle_active()
            else:
                analytic_accs.append(
                    self.env['account.analytic.account'].create({
                        'name': self.name + '-' + group.name,
                        'partner_id': self.id,
                        'expense_group_id': group.id,
                    }))
        if create_group:
            part_group = self.create_partition_group(analytic_accs)
        else:
            part_group = self.env['account.analytic.account'].search([
                ('partner_id', '=', self.id),
                ('partition_id', '!=', False)], limit=1).partition_id
            for acc in analytic_accs:
                self.create_partition_line(part_group, acc)
        return analytic_accs

    # def action_view_analytic_partition_lines(self):
    #     app_groups = list(map(lambda x: x.partition_id, self.env[
    #       'account.analytic.account'].search([('partner_id', '=', self.id)]))
    #         )
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Linhas de Rateio',
    #         'res_model': 'analytic.partition.line',
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'domain': [
    #             ('partition_id', 'in', [app.id for app in app_groups])],
    #     }

    def _update_analytic_accounts(self, groups):
        groups_to_remove = [item for item in self.expense_group_ids]
        groups_to_create = [item for item in groups]
        for item in self.expense_group_ids:
            for group in groups:
                if item == group:
                    groups_to_remove.remove(item)
                    groups_to_create.remove(group)
                    break
        if groups_to_create:
            self.create_analytic_account(groups_to_create)
        if groups_to_remove:
            self.deactivate_analytic_account(groups_to_remove)

    def _check_analytic_accounts(self, vals):
        groups = self.env['expense.group'].browse(
            vals['expense_group_ids'][0][2])
        if sorted(groups) != sorted(self.expense_group_ids):
            self._update_analytic_accounts(groups)
        part_group = self.env['account.analytic.account'].search([
            ('partner_id', '=', self.id),
            ('partition_id', '!=', False)], limit=1).partition_id
        part_group.calc_percent_by_employee()

    @api.multi
    def write(self, vals):
        if vals.get('expense_group_ids'):
            self._check_analytic_accounts(vals)
        res = super(ResPartner, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if vals.get('expense_group_ids') and res.is_branch:
            groups = self.env['expense.group'].browse(
                vals['expense_group_ids'][0][2])
            if groups:
                res.create_analytic_account(groups, True)
        return res


class ExpenseGroup(models.Model):
    _name = 'expense.group'

    name = fields.Char('Nome')

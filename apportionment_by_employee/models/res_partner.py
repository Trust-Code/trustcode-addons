# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    apportionment_ids = fields.Many2many(
        'analytic.apportionment', string='Grupos de Rateio')
    is_branch = fields.Boolean('É Filial')
    acc_group_ids = fields.Many2many('acc.group', string="Grupo de contas")
    count_apportionment_lines = fields.Integer(
        'Linhas de Rateio',
        compute="_compute_apportionment_lines")

    @api.multi
    def _compute_apportionment_lines(self):
        for item in self:
            app_groups = set(map(lambda x: x.apportionment_id, self.env[
                'account.analytic.account'].search(
                    [('partner_id', '=', item.id)])))
            item.count_apportionment_lines = sum(
                [len(app.apportionment_line_ids) for app in app_groups])

    def create_apportiomeint_group(self):
        analytic_accs = self.env['account.analytic.account'].search(
            [('partner_id', '=', self.id)])
        app_group = self.env['analytic.apportionment'].create({
            'name': 'Escritório ' + self.name,
            'apportionment_line_ids': [(0, 0, {
                'analytic_account_id': analytic_accs[0].id,
                'type': 'balance',
                'apportionment_percent': 0
            })]
        })
        for acc in analytic_accs[1:]:
            self.env['analytic.apportionment.line'].create({
                'apportionment_id': app_group.id,
                'analytic_account_id': acc.id,
                'type': 'percent',
                'apportionment_percent': 0
            })
        return app_group

    def create_analytic_account(self):
        if not self.acc_group_ids:
            raise UserError(
                'Selecione os grupos de conas para este escritório.')
        analytic_accs = []
        for group in self.acc_group_ids:
            analytic_accs.append(self.env['account.analytic.account'].create({
                'name': self.name + '-' + group.name,
                'partner_id': self.id,
            }))
        app_group = self.create_apportiomeint_group()
        for acc in analytic_accs:
            acc.write({'apportionment_id': app_group.id})

    def action_view_analytic_apportionment_lines(self):
        app_groups = list(map(lambda x: x.apportionment_id, self.env[
            'account.analytic.account'].search([('partner_id', '=', self.id)])))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Linhas de Rateio',
            'res_model': 'analytic.apportionment.line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [
                ('apportionment_id', 'in', [app.id for app in app_groups])],
        }

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        res.create_analytic_account()
        return res


class AccGroup(models.Model):
    _name = 'acc.group'

    name = fields.Char('Nome')

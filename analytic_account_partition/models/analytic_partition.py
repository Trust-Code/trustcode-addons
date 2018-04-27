# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import UserError


class AnalyticPartition(models.Model):
    _name = 'analytic.partition'

    name = fields.Char('Nome')
    partition_line_ids = fields.One2many(
        'analytic.partition.line',
        'partition_id',
        string="Linhas de Rateio")

    def _check_percent_amount(self):
        amount = 0
        for line in self.partition_line_ids:
            amount += line.partition_percent
        if amount > 100:
            raise UserError('O somatório do percentual de rateio é maior que\
                100%')
        return True

    def _check_analytic_accounts(self):
        if len(set([x.analytic_account_id for x in self.partition_line_ids]))\
                != len(self.partition_line_ids):
            raise UserError('Não podem existir duas linhas correspondentes à\
                mesma conta analítica')

    @api.model
    def create(self, vals):
        res = super(AnalyticPartition, self).create(vals)
        res._check_percent_amount()
        res._check_analytic_accounts()
        return res

    @api.multi
    def write(self, vals):
        res = super(AnalyticPartition, self).write(vals)
        self._check_percent_amount()
        self._check_analytic_accounts()
        return res


class AnalyticPartitionLine(models.Model):
    _name = 'analytic.partition.line'

    partition_id = fields.Many2one(
        'analytic.partition', string='Grupo de Rateio')
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Conta Analítica',
        ondelete='restrict')
    partition_percent = fields.Float('Percentual de Rateio', digits=(4, 4))
    isactive = fields.Boolean(
        string='Ativo', compute='_compute_is_active', store=True, default=True)

    @api.multi
    def _compute_is_active(self):
        for item in self:
            item.isactive = True
            if not item.analytic_account_id.active:
                item.isactive = False

# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import UserError


class AnalyticApportionment(models.Model):
    _name = 'analytic.apportionment'

    name = fields.Char('Nome')
    apportionment_line_ids = fields.One2many(
        'analytic.apportionment.line',
        'apportionment_id',
        string="Linhas de Rateio")

    def _check_percent_amount(self):
        balance_line = []
        amount = 0
        for line in self.apportionment_line_ids:
            if line.type == 'balance':
                balance_line.append(line)
            else:
                amount += line.apportionment_percent
        if len(balance_line) != 1:
            raise UserError('Uma (e apenas uma) linha de rateio deve ser do\
                tipo Saldo')
        else:
            balance_line[0].apportionment_percent = 100 - amount
        if amount > 100:
            raise UserError('O somatório do percentual de rateio é maior que\
                100%')

    @api.model
    def create(self, vals):
        res = super(AnalyticApportionment, self).create(vals)
        res._check_percent_amount()
        return res

    @api.multi
    def write(self, vals):
        res = super(AnalyticApportionment, self).write(vals)
        self._check_percent_amount()
        return res


class AnalyticApportionmentLine(models.Model):
    _name = 'analytic.apportionment.line'

    apportionment_id = fields.Many2one('analytic.apportionment', string='Grupo de Rateio')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Conta Analítica')
    type = fields.Selection([
        ('percent', 'Percentual'),
        ('balance', 'Saldo')],
        string="Tipo", default='percent')
    apportionment_percent = fields.Float('Percentual de Rateio', digits=(4, 4))

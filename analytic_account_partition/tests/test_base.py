# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from datetime import date


class TestBaseAnalyticPartition(TransactionCase):

    def setUp(self):
        super(TestBaseAnalyticPartition, self).setUp()
        self.main_company = self.env.ref('base.main_company')
        self.analytic_model = self.env['account.analytic.account']
        self.partition_model = self.env['analytic.partition']
        self.analytic_acc_one = self.analytic_model.create({
            'name': 'Analytic Account One'
        })
        self.analytic_acc_two = self.analytic_model.create({
            'name': 'Analytic Account Two'
        })
        self.analytic_acc_three = self.analytic_model.create({
            'name': 'Analytic Account Three'
        })
        self.analytic_acc_four = self.analytic_model.create({
            'name': 'Analytic Account Four'
        })
        self.partition_group = self.partition_model.create({
            'name': '213',
            'partition_line_ids': [
                (0, 0, {
                    'analytic_account_id': self.analytic_acc_one.id,
                    'partition_percent': 37.5698}),
                (0, 0, {
                    'analytic_account_id': self.analytic_acc_two.id,
                    'partition_percent': 28.5698})
            ]})
        self.analytic_acc_three.partition_id = self.partition_group
        self.expenses_account = self.env['account.account'].create({
            'code': '100',
            'name': 'Despesas',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id,
            'company_id': self.main_company.id
        })
        self.journal = self.env['account.journal'].create({
            'name': 'Expenses',
            'code': 'INV',
            'type': 'purchase',
            'default_debit_account_id': self.expenses_account.id,
            'default_credit_account_id': self.expenses_account.id,
        })
        self.move = self.env['account.move'].create({
            'name': 'Move name',
            'ref': 'Move one',
            'journal_id': self.journal.id,
            'line_ids': [
                (0, 0, {
                    'name': 'line one',
                    'account_id': self.expenses_account.id,
                    'debit': 3458.97,
                    'credit': 0,
                    'quantity': 1,
                    'date_maturity': date.today(),
                    'analytic_account_id': self.analytic_acc_three.id
                }),
                (0, 0, {
                    'name': 'line 2',
                    'account_id': self.expenses_account.id,
                    'debit': 0,
                    'credit': 3458.97,
                    'quantity': 1,
                    'date_maturity': date.today()
                })
            ]
        })

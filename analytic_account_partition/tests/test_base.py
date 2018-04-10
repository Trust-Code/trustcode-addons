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
        self.partition_model = self.env['analytic.account.partition']
        # self.product_one = self.env['product.product'].create({
        #     'name': 'Normal Product',
        #     'default_code': '010',
        #     'list_price': 99.53,
        #     'taxes_id': [],
        # })
        # self.product_two = self.env['product.product'].create({
        #     'name': 'Normal Product 2',
        #     'default_code': '011',
        #     'list_price': 37.13,
        #     'taxes_id': [],
        # })
        self.analytic_acc_one = self.analytic_model.create({
            'name': 'Analytic Account One'
        })
        self.analytic_acc_two = self.analytic_model.create({
            'name': 'Analytic Account Two'
        })
        self.analytic_acc_three = self.analytic_model.create({
            'name': 'Analytic Account Three'
        })
        self.partition_group = self.partition_model.create({
            'name': '213',
            'partition_line_ids': [
                (0, 0, {
                    'analytic_account_id': self.analytic_acc_one.id,
                    'type': 'percent',
                    'partition_percent': 37.5698}),
                (0, 0, {
                    'analytic_account_id': self.analytic_acc_two.id,
                    'type': 'percent',
                    'partition_percent': 28.5698}),
                (0, 0, {
                    'analytic_account_id': self.analytic_acc_three.id,
                    'type': 'balance'})
            ]})
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
            'ref': 'Move one',
            'journal_id': self.journal.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.expenses_account.id,
                    'debit': 3458.97,
                    'credit': 0,
                    'quantity': 1,
                    'date_maturity': date.today()
                }),
                (0, 0, {
                    'account_id': self.expenses_account.id,
                    'debit': 0,
                    'credit': 3458.97,
                    'quantity': 1,
                    'date_maturity': date.today()
                })
            ]
        })

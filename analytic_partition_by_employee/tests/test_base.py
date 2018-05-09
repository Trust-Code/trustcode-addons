# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from datetime import date


class TestBaseAnalyicEmploye(TransactionCase):

    def setUp(self):
        super(TestBaseAnalyicEmploye, self).setUp()
        self.main_company = self.env.ref('base.main_company')
        self.receivable_account = self.env['account.account'].create({
            'code': '1.0.0',
            'name': 'Conta de Recebiveis',
            'reconcile': True,
            'user_type_id': self.env.ref(
                'account.data_account_type_receivable').id,
            'company_id': self.main_company.id
        })
        self.group_one = self.env['expense.group'].create({
            'name': 'Grupo um'
        })
        self.group_two = self.env['expense.group'].create({
            'name': 'Grupo dois'
        })
        self.branch_one = self.env['res.partner'].create({
            'name': 'Nome Parceiro Um',
            'is_branch': True,
            'property_account_receivable_id': self.receivable_account.id,
            'expense_group_ids': [
                [6, 0, [self.group_one.id, self.group_two.id]]]
        })
        self.analytic_acc_one = self.env['account.analytic.account'].create({
            'name': 'Analytic Account One'
        })
        self.analytic_acc_two = self.env['account.analytic.account'].create({
            'name': 'Analytic Account Two'
        })
        self.partition_group = self.env['analytic.partition'].create({
            'name': '213',
            'partition_line_ids': [
                (0, 0, {
                    'analytic_account_id': self.analytic_acc_one.id,
                    'partition_percent': 37.5698}),
            ]})
        self.analytic_acc_two.partition_id = self.partition_group
        self.journal = self.env['account.journal'].create({
            'name': 'Receivable',
            'code': 'INV',
            'type': 'sale',
            'default_debit_account_id': self.receivable_account.id,
            'default_credit_account_id': self.receivable_account.id,
        })
        self.move = self.env['account.move'].create({
            'name': 'Move name',
            'ref': 'Move one',
            'journal_id': self.journal.id,
            'line_ids': [
                (0, 0, {
                    'name': 'line one',
                    'account_id': self.receivable_account.id,
                    'debit': 3458.97,
                    'credit': 0,
                    'quantity': 1,
                    'date_maturity': date.today(),
                    'analytic_account_id': self.analytic_acc_two.id,
                    'branch_partner_id': self.branch_one.id,
                }),
                (0, 0, {
                    'name': 'line 2',
                    'account_id': self.receivable_account.id,
                    'debit': 0,
                    'credit': 3458.97,
                    'quantity': 1,
                    'date_maturity': date.today(),
                    'branch_partner_id': self.branch_one.id
                })
            ]
        })
        for num in range(5):
            self.env['hr.employee'].create({
                'name': 'Empregado %d' % num,
                'analytic_account_ids': [(4, self.analytic_acc_one.id, 0)]
            })
        for num in range(11):
            self.env['hr.employee'].create({
                'name': 'Empregado %d' % num,
                'analytic_account_ids': [(4, self.analytic_acc_two.id, 0)]
            })

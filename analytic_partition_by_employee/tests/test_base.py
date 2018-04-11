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
        self.branch_one = self.env['res.partner'].create({
            'name': 'Nome Parceiro Um',
            'is_branch': True,
            'property_account_receivable_id': self.receivable_account.id,
            'acc_group_ids': [
                (0, 0, {
                    'name': 'Grupo um'
                }),
                (0, 0, {
                    'name': 'Grupo dois'
                })]
        })
        self.analytic_acc_one = self.env['account.analytic.account'].create({
            'name': 'Analytic Account One'
        })
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
                    'analytic_account_id': self.analytic_acc_one.id,
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
# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.analytic_partition_by_employee.tests.test_base import\
    TestBaseAnalyicEmploye


class TestResPartner(TestBaseAnalyicEmploye):

    def test_create(self):
        analytic_accs = self.env['account.analytic.account'].search([
            ('partner_id', '=', self.branch_one.id)])
        self.assertEquals(len(analytic_accs), len(
            self.branch_one.expense_group_ids))
        part_group = analytic_accs[0].partition_id
        self.assertEquals(len(part_group.partition_line_ids),
                          len(analytic_accs))

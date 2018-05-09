# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.analytic_partition_by_employee.tests.test_base import\
    TestBaseAnalyicEmploye


class TestAnalyticPartition(TestBaseAnalyicEmploye):

    def test_calc_percent_by_employee(self):
        self.partition_group.calc_percent_by_employee()
        line_one = self.partition_group.partition_line_ids.search(
            [('analytic_account_id', '=', self.analytic_acc_one.id)])
        self.assertEquals(line_one.partition_percent, round(5/16 * 100, 4))

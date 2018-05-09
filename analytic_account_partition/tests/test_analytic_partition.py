# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.analytic_account_partition.tests.test_base import\
    TestBaseAnalyticPartition
from odoo.exceptions import UserError


class TestAnalyticPartition(TestBaseAnalyticPartition):

    def test_check_percent_amount(self):
        with self.assertRaises(UserError) as f:
            self.partition_group.write({
                'partition_line_ids': [(0, 0, {
                    'analytic_account_id': self.analytic_acc_one.id,
                    'partition_percent': 1.5698})]
            })
        self.assertIn('mesma conta analítica', f.exception.name)
        self.partition_group.partition_line_ids[-1].unlink()
        with self.assertRaises(UserError) as f:
            self.partition_group.write({
                'partition_line_ids': [(0, 0, {
                    'analytic_account_id': self.analytic_acc_four.id,
                    'partition_percent': 100.5698})]
            })
        self.assertIn('100%', f.exception.name)
        self.partition_group.partition_line_ids[-1].unlink()


class TestAnalyticPartitionLine(TestBaseAnalyticPartition):

    def test_compute_is_active(self):
        partition_line = self.partition_group.partition_line_ids.search([
            ('analytic_account_id', '=', self.analytic_acc_one.id)])
        self.analytic_acc_one.active = False
        partition_line._compute_is_active()
        self.assertTrue(not partition_line.isactive)
        self.analytic_acc_one.active = True
        partition_line._compute_is_active()
        self.assertTrue(partition_line.isactive)

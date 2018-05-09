# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.analytic_account_partition.tests.test_base import\
    TestBaseAnalyticPartition


class TestAccountMove(TestBaseAnalyticPartition):

    def test_create_partition_move_lines(self):
        move_line = self.move.line_ids[0]
        lines = move_line._create_partition_move_lines(self.partition_group)
        amount = sum([line.credit for line in lines])
        self.assertEquals(round(amount, 2), 3458.97)
        self.assertTrue(len(lines) == len(
            self.partition_group.partition_line_ids) + 1)

    def test_post(self):
        self.move.post()
        credit = sum([line.credit for line in self.move.line_ids])
        debit = sum([line.debit for line in self.move.line_ids])
        self.assertEquals(round(credit, 2), round(debit, 2))

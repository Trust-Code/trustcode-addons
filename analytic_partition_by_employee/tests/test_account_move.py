# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.analytic_partition_by_employee.tests.test_base import\
    TestBaseAnalyicEmploye


class TestAccountMoveLine(TestBaseAnalyicEmploye):

    def test_create_partition_move_lines(self):
        app_group_one = self.env['account.analytic.account'].search([
            ('partner_id', '=', self.branch_one.id),
            ('partition_id', '!=', False)], limit=1).partition_id
        result = self.move.line_ids[1]._create_partition_move_lines(
            app_group_one)
        self.assertTrue(not result)
        # result = self.move.line_ids[0]._create_partition_move_lines(
        #     self.partition_group)
        # analytic_lines = [item.analytic_account_id for item in
        #                   self.partition_group.partition_line_ids]
        # for line in result:
        #     self.assertTrue(
        #         line.analytic_account_id not in analytic_lines)

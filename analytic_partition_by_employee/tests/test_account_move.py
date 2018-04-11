# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.analytic_partition_by_employee.tests.test_base import\
    TestBaseAnalyicEmploye


class TestAccountMoveLine(TestBaseAnalyicEmploye):

    def test_create_partition_move_lines(self):
        app_group = self.env['account.analytic.account'].search([
            ('partner_id', '=', self.branch_one.id)], limit=1).partition_id
        result = self.move.line_ids[0]._create_partition_move_lines(app_group)
        import ipdb
        ipdb.set_trace()
        self.assertTrue(result)

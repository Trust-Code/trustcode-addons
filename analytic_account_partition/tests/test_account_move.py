# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountMove(TransactionCase):

    def test_update_partition_move_line(self):
        credit = 54.72
        debit = 37.53
        percent = 37.4287
        move_line = self.env['account.move.line'].create({
            'name': 'teste',
            'credit': credit,
            'debit': debit,
        })
        partition_line = self.env['analytic.partition.line'].create({
            'type': 'percent',
            'partition_percent': percent
        })
        new_credit, new_debit = move_line.update_partition_move_line(
            move_line.credit,
            move_line.debit,
            partition_line)
        self.assertEquals(new_credit, round(credit*percent/100, 2))
        self.assertEquals(new_debit, round(debit*percent/100, 2))

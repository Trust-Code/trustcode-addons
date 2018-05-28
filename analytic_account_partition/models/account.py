# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    partition_id = fields.Many2one(
        'analytic.partition', 'Grupo de Rateio')

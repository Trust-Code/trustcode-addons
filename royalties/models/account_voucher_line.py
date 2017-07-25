# -*- coding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountVoucherLine(models.Model):
    _inherit = "account.voucher.line"

    fee = fields.Float(string="fee")

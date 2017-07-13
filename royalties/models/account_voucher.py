# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    royalties_id = fields.Many2one('royalties',
                                   string='Contrato Royalties',
                                   ondelete='restrict',
                                   domain="[('partner_id','=',partner_id),\
                                            ('state','=','in_progress')]")


class AccountVoucherLine(models.Model):
    _inherit = "account.voucher.line"

    inv_line_id = fields.Many2one('account.invoice.line')

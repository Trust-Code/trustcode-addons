# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    account_royalties_line_ids = fields.One2many('account.royalties.line',
                                                 'inv_line_id',
                                                 ondelete='set null')

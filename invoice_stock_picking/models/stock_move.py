# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    invoice_line_id = fields.Many2one(
        string="Invoice Line",
        comodel_name="account.invoice.line",)

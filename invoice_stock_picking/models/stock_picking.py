# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = ['stock.picking']

    invoice_id = fields.Many2one('account.invoice', string='Invoices',
                                 readolny=True)

# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    invoice_to = fields.Selection([
        ('partner', 'Para Cliente'),
        ('self', 'Próprio')],
        string='Faturamento',
        default='self')

    invoice_partner = fields.Many2one('res.partner', 'Faturar para')

    def close_order(self):
        self.write({'state': 'done'})

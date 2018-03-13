# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    invoice_to = fields.Selection([
        ('partner', 'Para Cliente'),
        ('self', 'Próprio')],
        string='Faturamento',
        default='self')

    invoice_partner = fields.Many2one('res.partner', 'Faturar para')

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.invoice_to == 'partner':
                order.write({'state': 'done'})
        return res

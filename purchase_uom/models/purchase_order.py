# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    second_qty = fields.Float('Segunda Quantidade')
    second_uom = fields.Many2one('product.uom', 'Segunda UOM')

    @api.onchange('product_id')
    def update_second_uom(self):
        if not self.product_id:
            self.update({
                'second_uom': False,
                'second_qty': False,
            })
            return
        p_uom = self.product_id.purchase_uom_id
        uom = self.product_id.uom_po_id
        self.second_uom = p_uom if p_uom != uom else False
        self.second_qty = self.product_qty * self.product_id.conversion_rate\
            if self.second_uom else False

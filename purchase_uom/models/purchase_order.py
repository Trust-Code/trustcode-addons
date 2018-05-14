# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    second_qty = fields.Float(
        'Segunda Quantidade',
        compute='update_second_uom')
    second_uom = fields.Many2one(
        'product.uom',
        'Segunda UOM',
        compute='update_second_uom')
    second_price_unit = fields.Float(
        'Segundo Preço Unitário',
        digits=(16, 4),
        compute='update_second_uom')

    def get_supplier_info(self):
        supplier_info = self.env['product.supplierinfo'].search(
            [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
             ('name', '=', self.order_id.partner_id.id)])
        noupdate = not (self.product_id and supplier_info.purchase_uom_id and
                        self.product_uom == supplier_info.product_uom)
        if noupdate:
            self.second_uom = False
            self.second_qty = False
            self.second_price_unit = False
            return
        return supplier_info

    @api.onchange('product_id', 'price_unit', 'product_qty', 'product_uom')
    def update_second_uom(self):
        supplier = self.get_supplier_info()
        if not supplier:
            return
        rate = supplier.conversion_rate
        self.second_uom = supplier.purchase_uom_id
        self.second_qty = self.product_qty * rate
        self.second_price_unit = self.valor_bruto / self.second_qty

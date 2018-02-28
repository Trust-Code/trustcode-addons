# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_tmpl_id = fields.Many2one('product.template')
    attr_sale = fields.One2many('sale.order.variant', 'so_line_id')

    @api.onchange('product_tmpl_id')
    def onchange_template(self):
        attribute_list = []
        for attribute_line in self.product_tmpl_id.attribute_line_ids:

            attribute_list.append({
                'attribute_id': attribute_line.attribute_id.id,
                'so_line_id': self.id,
            })
        self.attr_sale = [(0, 0, x) for x in attribute_list]

    @api.multi
    @api.onchange('attr_sale')
    def onchange_attr_sale(self):
        for item in self:
            for line in item.attr_sale:
                if not line.attr_value:
                    return
        domain = []
        for item in self.attr_sale.mapped('attr_value'):
            domain.append(('attribute_value_ids', '=', item.id))
        if domain:
            domain.append(('product_tmpl_id', '=', self.product_tmpl_id.id))
            product = self.product_id.search(domain)[0]
            self.update({
                'product_uom': product.uom_id.id,
                'product_id': product.id,
            })


class SaleOrderVariant(models.Model):
    _name = 'sale.order.variant'

    so_line_id = fields.Many2one('sale.order.line')
    attribute_id = fields.Many2one('product.attribute')
    attr_value = fields.Many2one('product.attribute.value')

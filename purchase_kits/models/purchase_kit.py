# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_kit = fields.Boolean(string=u"Is Kit?")
    kit_order_id = fields.Many2one(
        string="Purchase Order",
        comodel_name="purchase.order",
        ondelete="set null",
    )
    default_order_id = fields.Many2one(
        string="Purchase Order",
        comodel_name="purchase.order",
        ondelete="set null",
    )
    order_id = fields.Many2one(required=0)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.default_order_id:
            self.order_id = self.default_order_id
        elif self.kit_order_id:
            self.order_id = self.kit_order_id
        super(PurchaseOrderLine, self).onchange_product_id()

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        is_kit = True if self.order_id.is_kit else False
        for line in self.search([('order_id', '=', self.order_id.id),
                                ('is_kit', '=', is_kit)]):
            for val in line._prepare_stock_moves(picking):
                done += moves.create(val)
        return done

# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_kit = fields.Boolean(string="É kit?")
    purchase_kit_ids = fields.One2many(
        string=u"Kit's",
        comodel_name="purchase.order.line",
        inverse_name="kit_order_id",
    )
    order_line = fields.One2many(
        string='Order Lines',
        comodel_name='purchase.order.line',
        inverse_name='default_order_id',
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)]},
        copy=True)
    amount_untaxed_kit = fields.Monetary(
        string='Untaxed Amount',
        store=True,
        readonly=True,
        compute='_amount_all_kit',
        track_visibility='onchange')
    amount_tax_kit = fields.Monetary(
        string='Taxes',
        store=True,
        readonly=True,
        compute='_amount_all_kit')
    amount_total_kit = fields.Monetary(
        string='Total',
        store=True,
        readonly=True,
        compute='_amount_all_kit')

    @api.depends('purchase_kit_ids.price_total')
    def _amount_all_kit(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.purchase_kit_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                 'amount_untaxed_kit': order.currency_id.round(amount_untaxed),
                 'amount_tax_kit': order.currency_id.round(amount_tax),
                 'amount_total_kit': amount_untaxed + amount_tax,
            })

    @api.depends('order_line.move_ids.returned_move_ids',
                 'order_line.move_ids.state',
                 'order_line.move_ids.picking_id',
                 'purchase_kit_ids.move_ids.returned_move_ids',
                 'purchase_kit_ids.move_ids.state',
                 'purchase_kit_ids.move_ids.picking_id')
    def _compute_picking(self):
        for order in self:
            pickings = self.env['stock.picking']
            lines = order.order_line | order.purchase_kit_ids
            for l in lines:
                moves = l.move_ids | l.move_ids.mapped('returned_move_ids')
                pickings |= moves.mapped('picking_id')
            order.picking_ids = pickings
            order.picking_count = len(pickings)

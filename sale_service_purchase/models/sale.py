# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    @api.depends('order_line','order_line.is_po_created')
    def _check_is_po_created(self):
        for rec in self:
            for line in rec.order_line:
                if not line.is_po_created:
                    rec.so_created = True
    
    need_external_service = fields.Boolean(
        string='Is Need External Service?'
    )
    so_created = fields.Boolean(
        string='IS Sales Order Created?',
        compute='_check_is_po_created',
    )
    purchase_order_ids = fields.One2many(
        'purchase.order',
        'sale_order_id',
        string='Purchase Order'
    )
    
    @api.multi
    def get_purchase_order(self):
        for rec in self:
            purchase_orders = self.env['purchase.order'].search([('sale_order_id', '=', rec.id)])
            action = self.env.ref('purchase.purchase_form_action')
            result = action.read()[0]
            result.update({'domain': [('id', 'in', purchase_orders.ids)]})
        return result

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    is_po_created = fields.Boolean(
        string='Is PO Created',
        copy=False,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

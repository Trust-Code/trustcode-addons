# -*- coding: utf-8 -*-

from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Service Sales Order'
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    image_128 = fields.Image(string="Image")

    @api.onchange('product_id')
    def onchange_purchase_product_image(self):
    	for product in self:
    		product.image_128 = product.product_id.image_128
        
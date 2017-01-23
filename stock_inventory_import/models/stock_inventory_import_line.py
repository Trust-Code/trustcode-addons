# -*- coding: utf-8 -*-
# (c) 2015 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models


class StockInventoryImportLine(models.Model):
    _name = "stock.inventory.import.line"
    _description = "Stock Inventory Import Line"

    code = fields.Char('Product Code')
    product = fields.Many2one('product.product', 'Found Product')
    quantity = fields.Float('Quantity')
    inventory_id = fields.Many2one('stock.inventory', 'Inventory',
                                   readonly=True)
    location_id = fields.Many2one('stock.location', 'Location')
    lot = fields.Char('Product Lot')
    fail = fields.Boolean('Fail')
    fail_reason = fields.Char('Fail Reason')
    standard_price = fields.Float(string='Cost Price')

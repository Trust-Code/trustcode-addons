# -*- coding: utf-8 -*-
# (c) 2015 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models


class StockInventoryImportLine(models.Model):
    _name = "stock.inventory.import.line"
    _description = "Stock Inventory Import Line"

    code = fields.Char(string='Código do Produto')
    product = fields.Many2one('product.product', string='Produto')
    quantity = fields.Float(string='Quantidade')
    inventory_id = fields.Many2one('stock.inventory', string='Inventário',
                                   readonly=True)
    location_id = fields.Many2one('stock.location', string='Local')
    lot = fields.Char(string='Lote do Produto')
    fail = fields.Boolean(string='Erro')
    fail_reason = fields.Char(string='Status')
    list_price = fields.Float(string='Preço')
    owner_id = fields.Many2one('res.partner', string="Proprietário")

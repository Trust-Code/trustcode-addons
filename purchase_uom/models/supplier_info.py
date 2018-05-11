# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    purchase_uom_id = fields.Many2one(
            'product.uom', '2ª Unidade de Compra')
    conversion_rate = fields.Float(
        string='Fator de Conversão',
        help='Razão entre Unidade de Compra e a 2ª Unidade de compra.')
    new_price = fields.Float(
        'Novo preço unitário',
        compute='_compute_new_price',
        inverse='_set_main_price')

    @api.multi
    @api.onchange('price', 'conversion_rate')
    def _compute_new_price(self):
        for item in self:
            item.new_price = 0
            if item.conversion_rate:
                item.new_price = item.price / item.conversion_rate

    @api.multi
    @api.onchange('new_price', 'conversion_rate')
    def _set_main_price(self):
        for item in self:
            if item.conversion_rate:
                item.price = item.new_price * item.conversion_rate

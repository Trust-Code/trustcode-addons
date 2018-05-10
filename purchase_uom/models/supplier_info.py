# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    purchase_uom_id = fields.Many2one(
            'product.uom', '2ª Unidade de Compra')
    conversion_rate = fields.Float(
        string='Fator de Conversão',
        help='Razão entre Unidade de Compra e a 2ª Unidade de compra.')
    new_price_unit = fields.Float('Novo preço unitário')

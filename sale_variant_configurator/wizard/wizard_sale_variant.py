# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizardSaleVariantConfigurator(models.TransientModel):
    _name = 'wizard.sale.variant.configurator'

    owner_id = fields.Many2one(
        "sale.order.line", string="Owner")
    owner_model = fields.Char(required=True)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product Template',
        required=True)
    attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Attribute', readonly=True)
    value_id = fields.Many2one(
        comodel_name='product.attribute.value',
        domain="[('attribute_id', '=', attribute_id), "
               " ('id', 'in', possible_value_ids[0][2])]",
        string='Value')
    possible_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_compute_possible_value_ids')
    price_extra = fields.Float(
        compute='_compute_price_extra',
        help="Price Extra: Extra price for the variant with this attribute "
             "value on sale price. eg. 200 price extra, 1000 + 200 = 1200.")

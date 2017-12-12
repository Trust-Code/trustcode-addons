# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class DiscountRules(models.Model):
    _name = 'discount.rules'

    group_id = fields.Many2one('res.groups', string='Grupos')
    parcelas = fields.Integer(string='Parcelas')
    max_discount = fields.Float(string='Desconto')
    sale_config_id = fields.Many2one('sale.order.config')
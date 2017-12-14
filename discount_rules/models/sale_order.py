# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_max_discount(self):
        group = self.order_id.user_id.groups_id
        discount_rules = self.env['discount.rules'].search([]).filtered(
            lambda x: x.group_id in group)
        num_parcelas = len(self.order_id.payment_term_id.line_ids)
        max_discount = []
        if discount_rules:
            for rule in discount_rules:
                if rule.parcelas:
                    if num_parcelas <= rule.parcelas:
                        max_discount.append(rule.max_discount)
                else:
                    max_discount.append(rule.max_discount)
        return max_discount and max(max_discount) or 0.0

    @api.onchange('discount')
    def _check_discount(self):
        max_discount = self._get_max_discount()
        if self.discount > max_discount:
            return {
                'warning': {
                    'title': 'Atenção!',
                    'message':
                    u'O desconto informado está acima do valor permitido.'},
                'value': {
                    'discount': 0.0,
                }
            }

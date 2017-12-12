# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_max_discount(self):
        group = self.order_id.user_id.groups_id
        discount_rules = self.env['discount.rules'].search([]).filtered(
            lambda x: group in x.groups_id
        )
        num_parcelas = len(self.order_id.payment_term_id.line_ids)
        max_discount = []
        if discount_rules:
            for rule in discount_rules:
                if rule.parcelas:
                    if num_parcelas <= rule.parcelas:
                        max_discount.append(rule.max_discount)
                else:
                    max_discount.append(rule.max_discount)
        return max(max_discount)

    @api.onchange('discount')
    def _check_discount(self):
        max_discount = self._get_max_discount()
        if self.discount > max_discount:
            raise UserError(
                u'O desconto informado está acima do valor permitido.')

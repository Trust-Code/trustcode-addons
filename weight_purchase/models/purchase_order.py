# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('total_despesas', 'total_seguro', 'total_frete')
    def _onchange_despesas_frete_seguro(self):
        super(PurchaseOrder, self)._onchange_despesas_frete_seguro()
        full_weight = 0
        for line in self.order_line:
            if line.product_id.fiscal_type == 'product':
                full_weight += (line.product_id.weight * line.product_qty)
        for line in self.order_line:
            if line.product_id.fiscal_type == 'service':
                continue
            total_weight = (line.product_id.weight * line.product_qty)
            percentual = total_weight / full_weight
            line.update({
                'valor_frete': self.total_frete * percentual
            })

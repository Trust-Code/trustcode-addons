from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def merge_and_confirm_sale_order(self):
        orders = self.filtered(lambda x: x.state in ('draft', 'sent'))
        partners = orders.mapped('partner_id.commercial_partner_id')
        if len(partners) > 1:
            raise UserError('Apenas orçamentos para a mesma empresa podem ser confirmados')

        new_order = orders[0].copy({'order_line': []})

        for order in orders:
            for line in order.order_line:
                line.copy({'order_id': new_order.id})
            order.action_cancel()

        new_order.action_confirm()
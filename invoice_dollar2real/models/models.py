# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _prepare_invoice(self):
        currency = self.env['res.currency'].search([('name', '=', 'BRL')])
        inv = super(SaleOrder, self)._prepare_invoice()
        inv['currency_id']=currency.id
        return inv

class SaleOrderLine(models.Model):
    _inherit="sale.order.line"


    @api.multi
    def _prepare_invoice_line(self, qty):
        currency = self.env['res.currency'].search([('name', '=', 'BRL')])
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        import ipdb; ipdb.set_trace()
        if currency.id != self.order_id.pricelist_id.currency_id.id:
            res['price_unit']=res['price_unit']*currency.rate
        return res


#PREVIOUS ATEMPTS

# class SaleAdvancePaymentInv(models.TransientModel):
#     _inherit = "sale.advance.payment.inv"
#
#     @api.multi
#     def create_invoices(self):
#         sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
#         for order in sale_orders:
#             order.pricelist_id.currency_id = 3
#             for line in order.order_line:
#                 line.price_unit = line.price_unit*order.pricelist_id.currency_id.rate
#         if self.advance_payment_method == 'delivered':
#             sale_orders.action_invoice_create()
#         elif self.advance_payment_method == 'all':
#             sale_orders.action_invoice_create(final=True)
#         else:
#             # Create deposit product if necessary
#             if not self.product_id:
#                 vals = self._prepare_deposit_product()
#                 self.product_id = self.env['product.product'].create(vals)
#                 self.env['ir.values'].sudo().set_default('sale.config.settings', 'deposit_product_id_setting', self.product_id.id)
#
#             sale_line_obj = self.env['sale.order.line']
#             for order in sale_orders:
#                 if self.advance_payment_method == 'percentage':
#                     amount = order.amount_untaxed * self.amount / 100
#                 else:
#                     amount = self.amount
#                 amount = amount*order.pricelist_id.currency_id.rate
#                 if self.product_id.invoice_policy != 'order':
#                     raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
#                 if self.product_id.type != 'service':
#                     raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
#                 taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
#                 if order.fiscal_position_id and taxes:
#                     tax_ids = order.fiscal_position_id.map_tax(taxes).ids
#                 else:
#                     tax_ids = taxes.ids
#                 so_line = sale_line_obj.create({
#                     'name': _('Advance: %s') % (time.strftime('%m %Y'),),
#                     'price_unit': amount,
#                     'product_uom_qty': 0.0,
#                     'order_id': order.id,
#                     'discount': 0.0,
#                     'product_uom': self.product_id.uom_id.id,
#                     'product_id': self.product_id.id,
#                     'tax_id': [(6, 0, tax_ids)],
#                 })
#                 self._create_invoice(order, so_line, amount)
#         if self._context.get('open_invoices', False):
#             return sale_orders.action_view_invoice()
#         return {'type': 'ir.actions.act_window_close'}
#
#
#
#
#     # def _create_invoice(self, order, so_line, amount):
#     #     amount = amount*order.pricelist_id['BRL'].rate
#     #     so_line['price_unit'] = amount
#     #     invoice = super(SaleAdvancePaymentInv)._create_invoice(self, order, so_line, amount)
#     #     invoice['currency_id'] = 'BRL'
#     #     invoice.compute_taxes()
#     #     return invoice

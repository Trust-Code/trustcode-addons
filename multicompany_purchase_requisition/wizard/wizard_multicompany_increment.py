# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class WizardMulticompanyIncrement(models.TransientModel):
    _name = 'wizard.multicompany.increment'

    def _get_default_product(self):
        purchase_order_line_id = self.env['purchase.order.line'].browse(
            self.env.context.get('active_id'))
        return purchase_order_line_id.product_id

    def _get_default_product_uom(self):
        purchase_order_line_id = self.env['purchase.order.line'].browse(
            self.env.context.get('active_id'))
        return purchase_order_line_id.product_id.uom_id

    def _get_default_product_qty(self):
        purchase_order_line_id = self.env['purchase.order.line'].browse(
            self.env.context.get('active_id'))
        return purchase_order_line_id.prod_original_qty

    def _get_default_line(self):
        return self.env['purchase.order.line'].browse(
            self.env.context.get('active_id'))

    def _get_default_qty_increment(self):
        purchase_order_line_id = self.env['purchase.order.line'].browse(
            self.env.context.get('active_id'))
        return purchase_order_line_id.qty_increment

    @api.onchange('qty_increment')
    def _onchange_qty_increment(self):
        self.total_quantity = self.product_qty + self.qty_increment

    line_id = fields.Many2one('purchase.order.line', string="Attached Line",
                              default=_get_default_line)

    product_id = fields.Many2one(
        'product.product', string='Product',
        default=_get_default_product, readonly=True)
    product_uom_id = fields.Many2one(
        'product.uom', string='Product Unit of Measure',
        default=_get_default_product_uom, readonly=True)
    product_qty = fields.Float(
        string='Quantity', digits=dp.get_precision(
            'Product Unit of Measure'), default=_get_default_product_qty,
        readonly=True)
    qty_increment = fields.Float(
        string='Increment', digits=dp.get_precision(
            'Product Unit of Measure'),
        default=_get_default_qty_increment)

    total_quantity = fields.Float(
        string='Total Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True)

    @api.multi
    def action_confirm(self, vals):
        total_quantity = self.product_qty + self.qty_increment
        self.line_id.write({'qty_increment': self.qty_increment,
                            'product_qty': total_quantity})

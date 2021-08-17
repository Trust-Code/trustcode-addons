
from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrderLineItemRestore(models.TransientModel):
    _name = 'restore.sale.order.line.item'

    order_line_id = fields.Many2one('sale.order.line')
    name = fields.Text(related='order_line_id.name', readonly=True)
    product_id = fields.Many2one(
        related='order_line_id.product_id', readonly=True)
    product_uom_qty = fields.Float(
        related='order_line_id.product_uom_qty', readonly=True)
    price_unit = fields.Float(
        related='order_line_id.price_unit', readonly=True)
    discount = fields.Float(related='order_line_id.discount', readonly=True)
    currency_id = fields.Many2one(
        related='order_line_id.currency_id', readonly=True)
    price_subtotal = fields.Monetary(
        related='order_line_id.price_subtotal', readonly=True)
    selected = fields.Boolean("Selecionar")


class RestoreItemsWizard(models.TransientModel):
    _name = 'restore.items.wizard'

    order_id = fields.Many2one('sale.order')
    current_order_id = fields.Many2one('sale.order')
    line_ids = fields.Many2many('restore.sale.order.line.item')

    @api.onchange('order_id')
    def onchange_order_id(self):
        self.line_ids = [(0, False, {'order_line_id': x.id})
                         for x in self.order_id.order_line]

    def action_restore_all(self):
        if self.order_id.current_revision_id.state != 'draft':
            raise UserError(
                'Você pode restaurar apenas quando em provisório.\
                Crie uma nova versão antes!')
        self.order_id.current_revision_id.order_line.unlink()
        for item in self.line_ids:
            item.order_line_id.copy(
                {'order_id': self.order_id.current_revision_id.id})

    def action_restore_selected(self):
        if self.order_id.current_revision_id.state != 'draft':
            raise UserError(
                'Você pode restaurar apenas quando em provisório.\
                Crie uma nova versão antes!')
        for item in self.line_ids:
            if item.selected:
                item.order_line_id.copy(
                    {'order_id': self.order_id.current_revision_id.id})

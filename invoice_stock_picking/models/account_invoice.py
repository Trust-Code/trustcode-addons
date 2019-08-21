# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    @api.multi
    def action_invoice_open(self):
        if self.fiscal_position_id.picking_type_id:
            picking_type_id = self.fiscal_position_id.picking_type_id
            picking_id = self._prepare_stock_picking_vals(picking_type_id)
            picking_id = self.env['stock.picking'].create(picking_id)
            picking_id.action_confirm()

        return super(AccountInvoice, self).action_invoice_open()

    def _prepare_stock_picking_vals(self, picking_type_id):
        vals = {
            'partner_id': self.partner_id.id,
            'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'origin': self.number,
            'owner_id': self.partner_id.id,
            'picking_type_id': picking_type_id.id,
            'company_id': self.company_id.id,
            'invoice_id': self.id,
        }

        move_line_ids = []
        for item in self.invoice_line_ids:
            move_line_ids.append(
                (0, 0, self._prepare_stock_picking_line_vals(
                    item, picking_type_id)))

        vals['move_lines'] = move_line_ids

        return vals

    def _prepare_stock_picking_line_vals(self, invoice_line_id, pick_type_id):
        vals = {
            'product_id': invoice_line_id.product_id.id,
            'product_uom_qty': invoice_line_id.quantity,
            'product_uom': invoice_line_id.uom_id.id,
            'name': invoice_line_id.product_id.name,
            'invoice_line_id': invoice_line_id.id,
            'picking_type_id': pick_type_id.id,
        }

        return vals

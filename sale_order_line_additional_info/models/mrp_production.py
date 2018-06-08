from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    additional_info = fields.Text()

    @api.model
    def create(self, vals):
        if 'procurement_group_id' in vals and vals['procurement_group_id']:
            procurement_group_id = self.env['procurement.group'].browse(
                vals['procurement_group_id'])

            so_line = self.env['sale.order.line'].search([
                ('product_id', '=', vals['product_id']),
                ('product_uom_qty', '=', vals['product_qty']),
                ('order_id', '=', procurement_group_id.sale_id.id)], limit=1)

            if so_line:
                vals['additional_info'] = so_line.additional_info
        return super(MrpProduction, self).create(vals)

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    expedition_notes = fields.Text('Expedition Notes')

    @api.multi
    def action_confirm(self):
        for sale_order in self:
            res = super(SaleOrder, self).action_confirm()

            expedition_notes = sale_order.expedition_notes

            if expedition_notes:
                move_ids = self.picking_ids.filtered(
                    lambda x: x.state != 'cancel')
                for move in move_ids:
                    move.write({'expedition_notes': expedition_notes})
            return res

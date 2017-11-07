# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class StockPickingBatch(models.Model):
    _inherit = 'stock.location'

    picking_batch_id = fields.One2many(
        'picking.wave.rule', 'location_id', string='Picking Batch Rule')


class StockMove(models.Model):
    _inherit = 'stock.move'

    created_wave = fields.Boolean('Criado Onda')


class BatchProduct(models.Model):
    _name = 'picking.wave.rule'

    name = fields.Char("Name")
    location_id = fields.Many2one('stock.location', string='Local')
    picking_type_orig = fields.Many2one('stock.picking.type',
                                        string="Tipo de separação de origem")
    picking_type_dest = fields.Many2one('stock.picking.type',
                                        string="Tipo de separação de destino")

    def calculate_products_wave(self):
        product_obj = self.env['product.product']
        move_obj = self.env['stock.move']
        for rule in self.search([]):
            self.env.cr.execute("""
                SELECT product_id, SUM(product_uom_qty),
                       string_agg(reference, '; '), string_agg(id::text, ', ')
                FROM stock_move
                WHERE picking_type_id = %d
                    AND state LIKE 'confirmed'
                    AND created_wave = False
                GROUP BY product_id
                        """ % rule.picking_type_orig.id)

            lines = []
            move_ids = []
            origin = ""
            for l in self.env.cr.fetchall():
                move = move_obj.search([
                    ('product_id', '=', l[0]),
                    ('picking_type_id', '=', rule.picking_type_dest.id),
                    ('state', 'in', ['draft', 'confirmed',
                                     'partially_available'])
                ], limit=1)
                if move:
                    new_origin = move.origin + '; ' + l[2]
                    new_qty = move.product_uom_qty + l[1]
                    new_pick_origin = move.picking_id.origin + "; " + l[2]
                    move.write({'origin': new_origin,
                                'product_uom_qty': new_qty})
                    move.picking_id.write({'origin': new_pick_origin})
                else:
                    product_id = product_obj.browse(l[0])
                    product_uom_id = product_id.uom_id
                    lines.append([0, 0, {
                        'name': product_id.name,
                        'origin': l[2],
                        'product_id': l[0],
                        'product_uom_qty': l[1],
                        'product_uom': product_uom_id.id,
                        'picking_type_id': rule.picking_type_dest.id,
                    }])
                    origin += l[2] + "; "
                for x in l[3].split(','):
                    move_ids.append(int(x))

            picking_dest = rule.picking_type_dest
            vals = {
                'picking_type_id': picking_dest.id,
                'location_id': picking_dest.default_location_src_id.id,
                'location_dest_id': picking_dest.default_location_dest_id.id,
                'origin': origin,
                'move_lines': lines}
            self.env['stock.picking'].create(vals)
            move_obj.browse(move_ids).write({'created_wave': True})

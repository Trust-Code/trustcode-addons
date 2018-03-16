# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models, api


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

    @api.multi
    def calculate_products_wave(self):
        product_obj = self.env['product.product']
        move_obj = self.env['stock.move']
        for rule in self.search([]):
            self.env.cr.execute("""
                SELECT stock_move.product_id, SUM(stock_move.product_uom_qty),
                       string_agg(stock_picking.origin, '; '),
                       string_agg(stock_move.id::text, ', ')
                FROM stock_move
                INNER JOIN stock_picking
                on stock_picking.id = stock_move.picking_id
                WHERE stock_move.picking_type_id = %d
                    AND stock_move.state LIKE 'confirmed'
                    AND stock_move.created_wave = False
                GROUP BY stock_move.product_id
                        """ % rule.picking_type_orig.id)

            lines = []
            move_ids = []
            origin = ""
            picking_ids = []
            for l in self.env.cr.fetchall():
                move = move_obj.search([
                    ('product_id', '=', l[0]),
                    ('picking_type_id', '=', rule.picking_type_dest.id),
                    ('state', 'in', ['draft', 'confirmed',
                                     'partially_available'])
                ], limit=1)
                if move:
                    new_origin = move.origin + l[2] + "; "
                    new_qty = move.product_uom_qty + l[1]
                    new_pick_origin = (move.picking_id.origin if
                                       move.picking_id else "")
                    split_origin = l[2].split()
                    for item in split_origin:
                        if item not in new_pick_origin:
                            new_pick_origin += item + '; '
                    move.write({'origin': new_origin,
                                'product_uom_qty': new_qty})

                    move.picking_id.write({'origin': new_pick_origin})

                    if move.picking_id not in picking_ids:
                        picking_ids.append(move.picking_id)
                else:
                    product_id = product_obj.browse(l[0])
                    product_uom_id = product_id.uom_id
                    lines.append([0, 0, {
                        'name': product_id.name,
                        'origin': l[2] + '; ',
                        'product_id': l[0],
                        'product_uom_qty': l[1],
                        'product_uom': product_uom_id.id,
                        'picking_type_id': rule.picking_type_dest.id,
                    }])
                    origin += l[2] + "; "
                for x in l[3].split(','):
                    move_ids.append(int(x))

            origin = origin.split()
            new_origin = ""

            for item in origin:
                if item not in new_origin:
                    new_origin += item

            if len(lines) > 0:
                picking_dest = rule.picking_type_dest
                vals = {
                    'picking_type_id': picking_dest.id,
                    'location_id': picking_dest.default_location_src_id.id,
                    'location_dest_id':
                    picking_dest.default_location_dest_id.id,
                    'origin': new_origin,
                    'move_lines': lines}
                picking_ids.append(self.env['stock.picking'].create(vals))

            move_obj.browse(move_ids).write({'created_wave': True})

        if len(picking_ids) == 1:
            picking_id = picking_ids[0]
            dummy, act_id = self.env['ir.model.data'].get_object_reference(
                'stock', 'stock_picking_action_picking_type')
            dummy, view_id = self.env['ir.model.data'].get_object_reference(
                'stock', 'view_picking_form')
            vals = self.env['ir.actions.act_window'].browse(act_id).read()[0]
            vals['view_id'] = (view_id, 'view_picking_form')
            vals['views'][1] = (view_id, 'form')
            vals['views'] = [vals['views'][1], vals['views'][0]]
            vals['res_id'] = picking_id.id
            vals['context'] = {
                'default_picking_type_id': picking_id.picking_type_id.id}
            return vals
        elif len(picking_ids) > 1:
            picking_id = picking_ids[0]
            dummy, act_id = self.env['ir.model.data'].get_object_reference(
                'stock', 'stock_picking_action_picking_type')
            vals = self.env['ir.actions.act_window'].browse(act_id).read()[0]
            vals['context'] = {
                'default_picking_type_id': picking_id.picking_type_id.id}
            vals['domain'] = [('id', 'in', [x.id for x in picking_ids])]
            return vals

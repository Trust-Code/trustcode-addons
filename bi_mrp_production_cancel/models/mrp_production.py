# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
import math

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero



class AccountInvoice_Inherit(models.Model):
    _inherit = "account.move"

    active = fields.Boolean('Active', default=True, track_visibility=True)



class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'


    def post_inventory(self):

        for line in self.finished_move_line_ids :
            line.move_id.write({'mo_price_diff' :line.product_id.standard_price })


        res = super(MrpProduction, self).post_inventory()

        for line in self.finished_move_line_ids :
            line.move_id.write({'mo_price_diff' :line.product_id.standard_price - line.move_id.mo_price_diff })

        return res
    
    def action_cancel(self):
        """ Cancels production order, unfinished stock moves and set procurement
        orders in exception and Cancels production order which is Done."""
        for production in self:
            if production.state == 'done':
                move_obj = self.env['stock.move']
                pick_obj = self.env["stock.picking"]
                if production.move_finished_ids:
                    production.move_finished_ids.with_context(mrp=True).action_cancel()
                if production.move_raw_ids:
                    production.move_raw_ids.with_context(mrp=True).action_cancel()
                all_moves = (production.move_finished_ids | production.move_raw_ids)
                # cancel routing picking
                pickings = pick_obj.search([('origin', '=', production.name)])
                if pickings:
                    pick_obj.with_context(mrp=True).action_cancel([x.id for x in pickings])

                for move in all_moves :
                    account_move = self.env['account.move'].sudo().search([('stock_move_id','=',move.id)],order="id desc", limit=1)
                    if account_move :
                        account_move.button_cancel()
                        account_move.write({'active' : False})


                for fg in production.move_finished_ids :
                    if fg.product_id.categ_id.property_cost_method == 'average' :

                        new_std_price = fg.product_id.standard_price - fg.mo_price_diff

                        fg.product_id.with_context(force_company=fg.company_id.id).sudo().write({'standard_price': new_std_price})





            else:
                if any(workorder.state == 'progress' for workorder in self.mapped('workorder_ids')):
                    raise UserError(_('You can not cancel production order, a work order is still in progress.'))
                for production in self:
                    production.workorder_ids.filtered(lambda x: x.state != 'cancel').with_context(mrp=True).action_cancel()

                    finish_moves = production.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                    raw_moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                    (finish_moves | raw_moves).with_context(mrp=True)._action_cancel()

        self.write({'state': 'cancel', 'is_locked': True})

        return True


    
    def action_set_to_comfirmed(self):
        """ Cancels production order, unfinished stock moves and set procurement
        orders in exception """
        if not len(self.ids):
            return False
        move_obj = self.env['stock.move']
        for (ids, name) in self.name_get():
            message = _("Manufacturing Order '%s' has been set in confirmed state.") % name
            self.message_post(body = message)
        for production in self:
            all_moves = (production.move_finished_ids | production.move_raw_ids)
            all_moves.sudo().action_draft()
            production.write({'state': 'confirmed'})
        return True



class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def unlink(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        res = True
        for ml in self:
            if ml.state in ('done', 'cancel'):
                if self._context.get('mrp') == True :
                    pass
                else : 
                    raise UserError(_('You can not delete product moves if the picking is done. You can only correct the done quantities.'))
            # Unlinking a move line should unreserve.
            if ml.product_id.type == 'product' and not ml._should_bypass_reservation(ml.location_id) and not float_is_zero(ml.product_qty, precision_digits=precision):
                try:
                    self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                except UserError:
                    if ml.lot_id:
                        self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    else:
                        raise
        moves = self.mapped('move_id')
        if self._context.get('mrp') == True :
            pass
        else : 
            res = super(StockMoveLine, self).unlink()
        if moves:
            moves._recompute_state()
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'


    mo_price_diff = fields.Float(string='MO Price')



    def _action_cancel(self):
        return super(StockMove, self)._action_cancel()


    
    def action_draft(self):
        for move in self:
            res = move.write({'state': 'waiting'})
            move._do_unreserve()
        return res


    def _do_unreserve(self):
        Quant = self.env['stock.quant']
        if any(move.state in ('done',) for move in self):
            ml = self.mapped('move_line_ids')
            for line in ml:
                if self.raw_material_production_id:
                    Quant._update_available_quantity(line.product_id, line.location_id, line.qty_done, lot_id=line.lot_id, package_id=line.package_id, owner_id=line.owner_id)
                if self.production_id:
                    Quant._update_available_quantity(line.product_id, line.location_dest_id, -line.qty_done, lot_id=line.lot_id, package_id=line.package_id, owner_id=line.owner_id)
                self._recompute_state()
            self.mapped('move_line_ids').unlink()
        if any(move.state in ('cancel') for move in self):
            raise UserError(_('Cannot unreserve a done move'))
            self.mapped('move_line_ids').unlink()
        else:
            production_moves = self.filtered(lambda m: m.raw_material_production_id or m.production_id)
            production_moves._decrease_reserved_quanity(0.0)
            return super(StockMove, self - production_moves)._do_unreserve()            

    
    def action_cancel(self):
        """ Cancels the moves and if all moves are cancelled it cancels the picking. """
        # TDE DUMB: why is cancel_procuremetn in ctx we do quite nothing ?? like not updating the move ??
        Quant = self.env['stock.quant']
        if any(move.state == 'done' for move in self):
            for move in self:
                move._do_unreserve()
                siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                if move.propagate_cancel:
                    # only cancel the next move if all my siblings are also cancelled
                    if all(state == 'cancel' for state in siblings_states):
                        move.move_dest_ids._action_cancel()
                else:
                    if all(state in ('done', 'cancel') for state in siblings_states):
                        move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                        move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
            self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})


        if any(move.state == 'done' for move in self):
            raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))
            for move in self:
                if move.state == 'cancel':
                    continue
                move._do_unreserve()
                siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                if move.propagate_cancel:
                    # only cancel the next move if all my siblings are also cancelled
                    if all(state == 'cancel' for state in siblings_states):
                        move.move_dest_ids._action_cancel()
                else:
                    if all(state in ('done', 'cancel') for state in siblings_states):
                        move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                        move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
            self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
        return True


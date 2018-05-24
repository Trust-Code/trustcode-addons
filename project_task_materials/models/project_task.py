# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    material_project_task_ids = fields.One2many(
        'project.task.material', 'task_id', string='List of Materials')
    picking_counter = fields.Integer(
        'Picking Counter',
        compute="_compute_picking_counter")
    request_all = fields.Integer('Request Materials',
                                 compute="_compute_request_all")

    @api.multi
    def _compute_request_all(self):
        for item in self:
            if not item.material_project_task_ids:
                item.request_all = 0
            else:
                item.request_all = len(
                    self.env['project.task.material'].search([
                        ('requested', '=', False),
                        ('task_id', '=', item.id)]))

    def _get_picking_ids(self):
        pickings = []
        for material in self.material_project_task_ids:
            if material.move_id.picking_id:
                pickings.append(material.move_id.picking_id)
        return list(set(pickings))

    @api.multi
    def _compute_picking_counter(self):
        for item in self:
            item.picking_counter = len(item._get_picking_ids())

    @api.multi
    def action_view_delivery(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self._get_picking_ids()
        picking_ids = [item.id for item in pickings]
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', picking_ids)]
        elif pickings:
            action['views'] = [
                (self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = picking_ids[0]
        return action

    def action_request_all(self):
        request = []
        for item in self.material_project_task_ids:
            if not item.requested:
                request.append(item.id)
        self.write({
            'material_project_task_ids': [
                (1, id, {'requested': True}) for id in request]
        })

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        if vals.get('material_project_task_ids'):
            res.check_resquested_materials()
        return res

    @api.multi
    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if vals.get('material_project_task_ids'):
            self.check_resquested_materials()
        return res

    def create_analytic_line(self, material):
        unit = self.env.ref("product.product_uom_unit")
        line = self.env['account.analytic.line'].create({
            'name': '{} - {}'.format(material.product_id.name, self.name),
            'partner_id': self.partner_id.id,
            'account_id': material.task_id.project_id.analytic_account_id.id,
            'date': (datetime.date.today()).strftime('%Y-%m-%d'),
            'product_id': material.product_id.id,
            'unit_amount': material.quantity,
        })
        line.product_uom_id = material.product_id.uom_id or unit
        line.amount = material.product_id.lst_price * material.quantity
        return line

    def check_resquested_materials(self):
        pick_type = self.env.ref(
            'project_task_materials.stock_picking_type_materials')
        moves = []
        for material in self.material_project_task_ids:
            model_move = self.env['stock.move']
            if material.requested and not material.move_id:
                material.stage_requested = material.task_id.stage_id.name
                material.move_id = model_move.create({
                    'name': 'Material Item {}'.format(material.id),
                    'location_id': pick_type.default_location_src_id.id,
                    'location_dest_id': pick_type.default_location_dest_id.id,
                    'product_id': material.product_id.id,
                    'product_uom_qty': material.quantity,
                    'product_uom': material.product_id.uom_id.id,
                })
                moves.append(material.move_id)
                self.create_analytic_line(material)
            elif material.move_id and not material.requested:
                pick = material.move_id.picking_id
                material.move_id.unlink()
                material.stage_requested = ''
                if not pick.move_lines:
                    pick.unlink()
        if moves:
            vals = {
                'name': pick_type.sequence_id.next_by_id(),
                'partner_id': self.partner_id.id,
                'picking_type_id': pick_type.id,
                'location_id': pick_type.default_location_src_id.id,
                'location_dest_id': pick_type.default_location_dest_id.id,
            }
            picking = self.env['stock.picking'].create(vals)
            picking.move_lines = [(6, 0, [item.id for item in moves])]
            picking.action_confirm()
            picking.action_assign()

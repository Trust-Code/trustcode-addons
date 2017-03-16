# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    can_request_stock = fields.Boolean(string="Pode Solicitar Estoque?")

class ProjectProject(models.Model):
    _inherit = 'project.project'

    rule_id = fields.Many2one('procurement.rule', string='Regra Padrão')


class ProjectTaskMaterial(models.Model):
    _name = 'project.task.material'

    product_id = fields.Many2one('product.product', string='Produto', required=True)
    name = fields.Char(string="Name")
    stock_picking_id = fields.Many2one('stock.picking', string='Documento')
    stock_status = fields.Float(compute='_get_stock_status', string='Quantidade Entregue', readonly=True)
    stock_stage =  fields.Char(string='Estágio de Solicitação', readonly=True)
    quantity = fields.Float(string='Quantidade')
    requested = fields.Boolean(string="Solicitado")
    task_id = fields.Many2one('project.task', string='Tarefa')

    @api.model
    def create(self, vals):
        res = super(ProjectTaskMaterial, self).create(vals)
        res.stock_stage = res.task_id.stage_id.name
        return res

    # @api.depends('product_id.invoice_policy', 'order_id.state')
    def _get_stock_status(self):
        for item in self:
            procurement_ids = item.env['procurement.order'].search(
                [('task_id', '=', item.task_id.id)])
            qty = 0.0
            for move in procurement_ids.mapped('move_ids').filtered(lambda r: r.state == 'done' and not r.scrapped):
                if move.location_dest_id.usage == "customer":
                    qty += move.product_uom._compute_quantity(move.product_uom_qty)
                elif move.location_dest_id.usage == "internal" and move.to_refund_so:
                    qty -= move.product_uom._compute_quantity(move.product_uom_qty)
            item.stock_status = qty

class ProjectTask(models.Model):
    _inherit = 'project.task'

    material_project_task_ids = fields.One2many('project.task.material', 'task_id', string='Materiais Usados')

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        res.create_picking_from_material()
        return res

    @api.multi
    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        self.create_picking_from_material()
        return res

    def create_picking_from_material(self):
        for item in self:
            if not item.stage_id.can_request_stock:
                continue
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', item.company_id.id)], limit=1)
            for line in item.material_project_task_ids:
                if line.requested and not line.stock_picking_id:    
                    if line.product_id.qty_available <= line.quantity:
                        procurement_id = self.env['procurement.order'].create({
                                'product_id': line.product_id.id,
                                'product_uom': line.product_id.uom_id.id,
                                'product_qty': line.quantity,
                                'origin': item.name,
                                'task_id': item.id,
                                'name': item.name,
                                'rule_id': item.project_id.rule_id.id,
                                'company_id': item.company_id.id,
                                'warehouse_id': warehouse.id,
                                'location_id': warehouse.lot_stock_id.id,
                                })

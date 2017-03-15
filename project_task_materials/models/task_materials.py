# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    can_request_stock = fields.Boolean(string="Pode Solicitar Estoque?")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    material_ids = fields.One2many(
        comodel_name="project.task.material",
        inverse_name="materials", string="Material")

    product_id = fields.Many2one(
        string="Produto", comodel_name="account.invoice",
        related="product.product",
        store=True)
    sale_order = fields.Many2one(
        string="Ordem de Compra", comodel_name="account.invoice",
        related="sale.order",
        store=True)
    lot_id = fields.Many2one(
        string="Nº Kanban", comodel_name="account.invoice",
        related="stock.production.lot",
        store=True)

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        self.create_picking_from_material()
        return res

    @api.multi
    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        self.create_picking_from_material()
        return res

    # def create_picking_from_material(self):
    #     self.search([]).write({'name'?})

    #     for item in self:
    #         if item.stage_id.x_can_request_stock:
    #     '''    
    #     stock_picking = env['stock.picking'].create({
    #          'location_id':15 if obj.company_id.id==1 else 29,
    #          'location_dest_id': 20,
    #          'picking_type_id': 7, # 1 if obj.company_id.id==1 else 10,
    #          'move_type': 'one',
    #          'priority': '1',
    #          'origin':obj.name,
    #          'name':obj.name,
    #          })
    #     '''
    #     for line in obj.x_material_ids:
    #         if line.x_requested and not line.x_stock_picking_id:
                
    #             if line.x_product_id.qty_available <= line.x_quantity:
    #                 procurement_order_id = env['procurement.order'].create({
    #                                             'product_id':line.x_product_id.id,
    #                                             'product_uom':line.x_product_id.uom_id.id,
    #                                             'product_qty':line.x_quantity, # - line.x_product_id.qty_available,
    #                                             'origin':obj.name,
    #                                             'task_id':obj.id,
    #                                             'name':obj.name,
    #                                             'rule_id':23, #5 if obj.company_id.id==1 else 16,
    #                                             'company_id':obj.company_id.id,
    #                                             'warehouse_id':1 if obj.company_id.id==1 else 2,
    #                                             'location_id':15 if obj.company_id.id==1 else 29,
    #                                             })
    #             '''
    #             stock_picking.write({
    #                                 'move_lines':[[0,0,{
    #                                    'name':line.x_product_id.name,
    #                                    'product_id':line.x_product_id.id,
    #                                    'product_uom_qty':line.x_quantity,
    #                                    'product_uom':line.x_product_id.uom_id.id,
    #                                    'location_id':15 if obj.company_id.id==1 else 29,
    #                                    'location_dest_id': 20,
    #                                                  }]],
    #                                 })
    #             '''            
    #             line.write({'x_stock_picking_id':procurement_order_id.id})
    # #    stock_picking.action_confirm()
    # #    stock_picking.action_assign()





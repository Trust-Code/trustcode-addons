# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or latres (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    can_request_stock = fields.Boolean(string="Pode Solicitar Estoque?")


class ProjectProject(models.Model):
    _inherit = 'project.project'

    rule_id = fields.Many2one('procurement.rule', string='Regra Padrão')


class ProjectTaskMaterial(models.Model):
    _name = 'project.task.material'

    product_id = fields.Many2one(
        'product.product', string='Produto', required=True)
    name = fields.Char(string="Name")
    procurement_id = fields.Many2one('procurement.order', string='Documento')
    qty_delivered = fields.Float(
        compute='_get_stock_status',
        string='Quantidade Entregue', readonly=True)
    qty_stock_available = fields.Float(
        compute='_get_stock_product_available',
        string='Quantidade Disponível', readonly=True)
    stock_stage = fields.Char(string='Estágio de Solicitação', readonly=True)
    quantity = fields.Float(string='Quantidade')
    requested = fields.Boolean(string="Solicitado")
    task_id = fields.Many2one('project.task', string='Tarefa')

    @api.model
    def create(self, vals):
        res = super(ProjectTaskMaterial, self).create(vals)
        res.stock_stage = res.task_id.stage_id.name
        return res

    def _get_stock_status(self):
        stock_move_operation_link = self.env['stock.move.operation.link']
        for item in self:
            procurement_ids = self.env['procurement.order'].search(
                [('material_project_task_id.id', '=', item.id)])
            for line in procurement_ids:
                operation_move_link_ids = stock_move_operation_link.search(
                    [('move_id.procurement_id', '=', line.id)])
                qty_done = 0
                for x in operation_move_link_ids:
                    qty_done += x.operation_id.qty_done
                item.qty_delivered = qty_done

    def _get_stock_product_available(self):
        for item in self:
            qty_available = item.product_id.qty_available
            item.qty_stock_available = qty_available

    @api.multi
    def name_get(self):
        res = []
        for item in self:
            res.append((item.id, "%s" % (item.product_id.name)))
        return res


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sale_order_id = fields.Many2one('sale.order', string="Pedido")
    material_project_task_ids = fields.One2many(
        'project.task.material', 'task_id', string='Materiais Usados')

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
            warehouse = self.env['stock.warehouse'].search(
                [('company_id', '=', item.company_id.id)], limit=1)
            group_id = self.env['procurement.group'].create(
                {'name': item.name, 'move_type': 'direct'}
            )
            for line in item.material_project_task_ids:
                if line.requested and not line.procurement_id:
                    vals = {
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'product_qty': line.quantity,
                        'origin': item.name,
                        'task_id': item.id,
                        'name': item.name,
                        'rule_id': item.project_id.rule_id.id,
                        'company_id': item.company_id.id,
                        'warehouse_id': warehouse.id,
                        'location_id': item.project_id.rule_id.location_id.id,
                        'material_project_task_id': line.id,
                        'group_id': group_id.id,
                    }
                    procurement = self.env['procurement.order'].create(vals)
                    line.procurement_id = procurement.id


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    material_project_task_id = fields.Many2one(
        'project.task.material', 'Linha de material na tarefa')

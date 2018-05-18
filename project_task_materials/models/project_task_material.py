# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectTaskMaterial(models.Model):
    _name = 'project.task.material'

    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    name = fields.Char(string="Name")
    picking_id = fields.Many2one('stock.picking', string='')
    qty_delivered = fields.Float(
        compute='_get_stock_status',
        string='Delivered Quantity', readonly=True)
    qty_stock_available = fields.Float(
        compute='_get_stock_product_available',
        string='Quantity On Hand', readonly=True)
    quantity = fields.Float(string='Quantity')
    requested = fields.Boolean(string="Requested")
    task_id = fields.Many2one('project.task', string='Task')
    stage_requested = fields.Char('Requested on stage', readonly=True)

    @api.multi
    def _get_stock_status(self):
        for item in self:
            move_id = self.env['stock.move'].search(
                [('material_project_task_id', '=', item.id)])
            item.qty_delivered = move_id.quantity_done

    @api.multi
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

    @api.multi
    def unlink(self):
        self.env['stock.move'].search(
            [('material_project_task_id', 'in', self.ids)]).unlink()
        return super(ProjectTaskMaterial, self).unlink()

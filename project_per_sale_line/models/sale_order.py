# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_tracking = fields.Selection(selection_add=[
        ('new_project_per_line', 'Cria um projeto por linha da venda'),
        ('new_project_per_line_plus_task', 'Cria um projeto por linha da venda\
            + tarefa')])


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_project_ids(self):
        for order in self:
            projects = order.order_line.mapped('product_id.project_id')
            projects |= order.order_line.mapped('project_id')
            if order.project_project_id:
                projects |= order.project_project_id
            order.project_ids = projects


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    project_id = fields.Many2one('project.project', 'Projeto')

    def _timesheet_create_task_prepare_values(self):
        v = super(SaleOrderLine, self)._timesheet_create_task_prepare_values()
        if self.product_id.service_tracking ==\
                'new_project_per_line_plus_task':
            v['project_id'] = self.project_id.id
        return v

    def _timesheet_create_project(self, task=False):

        Project = self.env['project.project']
        name = (self.product_id.default_code or None
                ) + ": " + self.order_id.name
        project_id = Project.create({
            'name': name,
            'code': self.order_id.client_order_ref,
            'company_id': self.order_id.company_id.id,
            'partner_id': self.order_id.partner_id.id,
            'sale_line_id': self.id
        })
        self.project_id = project_id.id
        if task:
            self._timesheet_create_task()

    @api.multi
    def _timesheet_service_generation(self):
        super(SaleOrderLine, self)._timesheet_service_generation()
        for so_line in self.filtered(lambda sol: sol.is_service):
            # create a new project
            if so_line.product_id.service_tracking == 'new_project_per_line':
                so_line._timesheet_create_project()
            if so_line.product_id.service_tracking ==\
                    'new_project_per_line_plus_task':
                so_line._timesheet_create_project(task=True)

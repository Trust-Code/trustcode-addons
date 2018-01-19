# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_tracking = fields.Selection(selection_add=[
        ('new_project_per_line', 'Cria um projeto por linha da venda')])


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
        if self.product_id.service_tracking == 'new_project_per_line':
            v['project_id'] = self.project_id.id
        return v

    def _timesheet_create_project(self):
        Project = self.env['project.project']
        self.order_id._create_analytic_account(
            prefix=self.product_id.default_code or None)
        account = self.order_id.analytic_account_id
        project = Project.search(
            [('analytic_account_id', '=', account.id)], limit=1)
        self.project_id = project.id
        self._timesheet_create_task()

    @api.multi
    def _timesheet_service_generation(self):
        super(SaleOrderLine, self)._timesheet_service_generation()
        for so_line in self.filtered(lambda sol: sol.is_service):
            # create a new project
            if so_line.product_id.service_tracking == 'new_project_per_line':
                so_line._timesheet_create_project()

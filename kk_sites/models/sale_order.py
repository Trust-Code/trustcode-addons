# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    kk_site_id = fields.Many2one('kk.sites', string="Site")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_find_project(self):
        project = super(SaleOrderLine, self)._timesheet_find_project()
        project.write({'kk_site_id': self.order_id.kk_site_id.id})
        return project

    @api.multi
    def _timesheet_find_task(self):
        result = super(SaleOrderLine, self)._timesheet_find_task()
        for so_line in self:
            task = result[so_line.id]
            task.write({'kk_site_id': so_line.order_id.kk_site_id.id})
        return result


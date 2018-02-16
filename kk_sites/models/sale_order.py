# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    kk_site_id = fields.Many2one('kk.sites', string="Site")

    @api.multi
    def _timesheet_find_task(self):
        result = super(SaleOrderLine, self)._timesheet_find_task()
        for so_line in self:
            task = result[so_line.id]
            task.write({'kk_site_id': so_line.kk_site_id.id})
        return result

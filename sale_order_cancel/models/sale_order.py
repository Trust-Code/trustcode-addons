# -*- coding: utf-8 -*-
# © 2018 Guilherme Lenon da Silva, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_cancel(self):
        for item in self:
            work_order = self.env['mrp.production'].search(
                [('procurement_group_id', '=', item.procurement_group_id.id)])
            work_order.action_cancel()
            item.tasks_ids.write({'active': False})
            projects = item.mapped('order_line.product_id.project_id')
            projects = item.project_ids - projects
            projects.write({'active': False})
        return super(SaleOrder, self).action_cancel()

# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class SaleOrderReport(models.Model):
    _name = 'sale.order.report'
    _description = u'Sale Order Report'

    name = fields.Char(string='Nome', size=60)
    description = fields.Html('Description')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _description_default(self):
        return self.env['sale.order.report'].search([], limit=1)

    description_report = fields.Many2one(
        'sale.order.report',
        string='Report Description',
        help=u'Select a custom description report.',
        default=_description_default
    )

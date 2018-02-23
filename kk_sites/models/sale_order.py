# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    kk_site_id = fields.Many2one('kk.sites', string="Site")

    description_proposta = fields.Html(string="Descrição para proposta")

    @api.multi
    def _timesheet_find_task(self):
        result = super(SaleOrderLine, self)._timesheet_find_task()
        for so_line in self:
            task = result[so_line.id]
            task.write({'kk_site_id': so_line.kk_site_id.id,
                        'name': '%s:%s' % (so_line.order_id.name,
                                           so_line.product_id.name)})
        return result

    @api.onchange('product_id')
    def _onchange_product(self):
        setattr(self, 'description_proposta',
                self.product_id.description_proposta)

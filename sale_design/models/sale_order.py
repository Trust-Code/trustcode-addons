# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import RedirectWarning


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('design', 'Design'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True,
        track_visibility='onchange', default='draft')

    def to_design(self):
        for line in self.order_line:
            if not line.product_id.allow_design:
                action = self.env.ref('product.product_template_action_all')
                msg = "Não é permitido o design do item %s. Para\
                        habilitar esta opção acesse o cadastro do produto,\
                        'Faturamento' e selecione a opção 'Permitir Design'"\
                        % line.product_id.name
                raise RedirectWarning(msg, action.id, 'Acesse os produtos')
        self.order_line._timesheet_service_generation(design=True)
        self.write({'state': 'design'})


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _timesheet_service_generation(self, design=False):
        if not design:
            return
        else:
            super(SaleOrderLine, self)._timesheet_service_generation()

# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def project_create(self, vals):
        # Impede que sejam criadas dois projetos quando uma cotação com itens
        # recorrentes é confirmada
        order = self.env['sale.order'].search([('project_id', '=', self.id)])
        if order.is_contract:
            return False
        return super(AccountAnalyticAccount, self).project_create(vals)


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _create_service_task(self):
        # Impede que sejam criadas duas tarefas quando uma cotação com itens
        # recorrentes é confirmada
        order = self.sale_line_id.order_id
        if order.is_contract:
            return False
        return super(ProcurementOrder, self)._create_service_task()

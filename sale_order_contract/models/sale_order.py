# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_start_contract(self):
        return date.today()

    def _compute_end_contract(self):
        return date.today() + relativedelta(years=1)

    recurring_contract = fields.Boolean(string="Possui Contrato?")
    active_contract = fields.Boolean(string="Contrato Ativo?", copy=False)

    invoice_period = fields.Selection(
        [('monthly', 'Mensal'), ('annual', 'Anual')],
        string="Período Faturamento")
    start_contract = fields.Date(
        string="Inicio Contrato", default=_compute_start_contract)
    end_contract = fields.Date(
        string="Final Contrato", default=_compute_end_contract)
    next_invoice = fields.Date(string="Próximo Faturamento", copy=False)

    @api.multi
    def action_invoice_contracts(self):
        sale_orders = self.search([('active_contract', '=', True),
                                   ('next_invoice', '=', date.today())])

        for order in sale_orders:

            new_order = order.copy({
                 'recurring_contract': False,
                 'active_contract': False,
                 'invoice_period': None,
                 'start_contract': None,
                 'end_contract': None,
                 'origin': order.name,
                 })
            last_invoice = fields.Date.from_string(order.next_invoice)
            order.next_invoice = date.today() + relativedelta(
                months=1, day=last_invoice.day)
            new_order.action_confirm()
            new_order.action_invoice_create(final=True)

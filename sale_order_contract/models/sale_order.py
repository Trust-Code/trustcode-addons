# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil import parser
from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_start_contract(self):
        return date.today()

    def _compute_end_contract(self):
        return date.today() + relativedelta(years=1)

    @api.depends('order_line.price_subtotal')
    def _compute_total_values(self):
        for order in self:
            recurrent = order.order_line.filtered(lambda x: x.recurring_line)
            non_rec = order.order_line.filtered(lambda x: not x.recurring_line)
            order.total_recurrent = sum(l.price_subtotal for l in recurrent)
            order.total_non_recurrent = sum(l.price_subtotal for l in non_rec)

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
    total_recurrent = fields.Monetary(
        string="Total Recorrente", compute='_compute_total_values',
        store=True)
    total_non_recurrent = fields.Monetary(
        string="Total Avulso", compute='_compute_total_values', store=True)
    margin_recurrent = fields.Float(
        string="Margem do Recorrente (%)",
        compute='_compute_margin_percentage',
        store=True)
    margin_non_recurrent = fields.Float(
        string="Margem do Avulso (%)",
        compute='_compute_margin_percentage',
        store=True)

    @api.onchange('order_line')
    def _onchange_sale_order_contract_order_line(self):
        recurring = False
        for item in self.order_line:
            if item.recurring_line:
                recurring = True
                break
        self.recurring_contract = recurring

    @api.onchange('active_contract')
    def _onchange_active_contract(self):
        if self.active_contract and not self.next_invoice:
            self.next_invoice = parser.parse(self.start_contract) + \
                relativedelta(months=1)

    @api.multi
    def action_view_contract_orders(self):
        orders = self.search([('origin', '=', self.name)])
        action = self.env.ref('sale.action_orders').read()[0]
        if len(orders) > 0:
            action['domain'] = [('id', 'in', orders.ids)]
        else:
            raise UserError('Nenhum pedido encontrado!')
        return action

    @api.multi
    def action_invoice_contracts(self):
        sale_orders = self.search([('active_contract', '=', True),
                                   ('next_invoice', '=', date.today()),
                                   ('state', '=', 'sale')])
        for order in sale_orders:
            end_contract = fields.Date.from_string(order.end_contract)
            if end_contract < date.today():  # Cancelar contrato
                order.active_contract = False
                order.next_invoice = False
                continue

            new_order = order.copy({
                'recurring_contract': False,
                'active_contract': False,
                'invoice_period': None,
                'start_contract': None,
                'end_contract': None,
                'origin': order.name,
                'client_order_ref': 'Contrato ' + order.name,
            })
            non_recurrent_lines = filter(lambda line: not line.recurring_line,
                                         new_order.order_line)
            map(lambda line: line.unlink(), non_recurrent_lines)
            last_invoice = fields.Date.from_string(order.next_invoice)
            order.next_invoice = date.today() + relativedelta(
                months=1, day=last_invoice.day)
            new_order.action_confirm()
            new_order.action_invoice_create(final=True)
            new_order.action_done()

    @api.multi
    def _get_next_month(self):
        for order in self:
            order.next_month = date.today() + relativedelta(months=1)

    next_month = fields.Date(string="Next Month", compute='_get_next_month')

    @api.depends('order_line.margin', 'total_recurrent', 'total_non_recurrent')
    def _compute_margin_percentage(self):
        for order in self:
            recurrent = sum(order.order_line.filtered(
                lambda x: x.recurring_line).mapped('margin'))
            non_rec = sum(order.order_line.filtered(
                lambda x: not x.recurring_line).mapped('margin'))

            if order.total_recurrent != 0:
                order.margin_recurrent = (
                    recurrent / order.total_recurrent) * 100

            if order.total_non_recurrent != 0:
                order.margin_non_recurrent = (
                    non_rec / order.total_non_recurrent) * 100


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_sale_order_contract_product_id(self):
        self.recurring_line = self.product_id.recurring_product

    recurring_line = fields.Boolean(string="Recorrente?")

    @api.depends('product_id', 'purchase_price', 'product_uom_qty',
                 'price_unit', 'discount')
    def _product_margin(self):
        return super(SaleOrderLine, self)._product_margin()

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

    @api.multi
    def _get_next_month(self):
        for order in self:
            order.next_month = date.today() + relativedelta(months=1)

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
        [('1', 'Mensal'),('6','Semestral'),('12', 'Anual')],
        string="Período Faturamento",
        default='1',
        track_visibility='onchange')
    start_contract = fields.Date(
        string="Inicio Contrato",
        track_visibility='onchange',
        default=date.today())
    end_contract = fields.Date(
        string="Final Contrato",
        track_visibility='onchange',
        default=date.today() + relativedelta(years=1))
    next_invoice = fields.Date(string="Próximo Faturamento", copy=False)
    total_recurrent = fields.Monetary(
        string="Total Recorrente",
        store=True,
        compute='_compute_total_values',
        track_visibility='onchange')
    total_non_recurrent = fields.Monetary(
        string="Total Avulso",
        store=True,
        compute='_compute_total_values',
        track_visibility='onchange')
    margin_recurrent = fields.Float(
        string="Margem do Recorrente (%)",
        compute='_compute_margin_percentage',
        track_visibility='onchange',
        store=True)
    margin_non_recurrent = fields.Float(
        string="Margem do Avulso (%)",
        track_visibility='onchange',
        compute='_compute_margin_percentage',
        store=True)
    next_month = fields.Date(string="Next Month", compute='_get_next_month')
    is_contract= fields.Boolean("Just Contract")

    @api.onchange('order_line')
    def _onchange_product_id(self):
        if filter(lambda item:item.recurring_line==True,self.order_line):
            self.recurring_contract=True

    @api.onchange('active_contract','invoice_period')
    def _onchange_active_contract(self):
        if self.invoice_period:
            add = relativedelta(months=int(self.invoice_period))
            self.next_invoice = parser.parse(self.start_contract) + add
        if not self.active_contract: self.next_invoice=False

    def _create_contract(self):
        payment_term=self.env['account.payment.term']
        new_order = self.copy({
        'origin': self.name,
        'client_order_ref': 'Contrato ' + self.name,
        'payment_term_id':payment_term.search([('indPag','=','0')], limit=1).id,
        'is_contract':True,
        })
        non_recurrent_lines = filter(lambda line: not line.recurring_line,
                                     new_order.order_line)
        map(lambda line: line.unlink(), non_recurrent_lines)

    @api.multi
    def action_confirm(self):
        '''
            Verifica se possui venda de produto recorrente.
            Caso positivo, duplica a cotação e leva os proudutos com recorrencia para a nova cotação.
        '''
        res = super(SaleOrder, self).action_confirm()
        recurrent_lines=map(lambda line:line.recurring_line, self.order_line)
        if recurrent_lines and False in recurrent_lines:
            self._create_contract()
        else:
            payment_term=self.env['account.payment.term']
            self.env['account.payment.term'].search([('indPag','=','0')], limit=1).id
            self.write({'is_contract':True,
                        'payment_term_id':payment_term.search(
                                        [('indPag','=','0')],
                                        limit=1).id})
        return res

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

            last_invoice = fields.Date.from_string(order.next_invoice)
            order.next_invoice = date.today() + relativedelta(
                months=1, day=last_invoice.day)
            self.action_invoice_create(final=True)
            # Set qty_invoiced as Null to possible invoicing again
            for line in self.order_line:line.qty_invoiced=0

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

    recurring_line = fields.Boolean(string="Recorrente?",
        related="product_id.recurring_product")

    @api.depends('product_id', 'purchase_price', 'product_uom_qty',
                 'price_unit', 'discount')
    def _product_margin(self):
        return super(SaleOrderLine, self)._product_margin()

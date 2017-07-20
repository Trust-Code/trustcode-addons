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

    @api.depends('order_line.price_subtotal')
    def _compute_total_values(self):
        for order in self:
            recurrent = order.order_line.filtered(lambda x: x.recurring_line)
            non_rec = order.order_line.filtered(lambda x: not x.recurring_line)
            order.total_recurrent = sum(l.price_subtotal for l in recurrent)
            order.total_non_recurrent = sum(l.price_subtotal for l in non_rec)

    recurring_contract = fields.Boolean(string="Possui Contrato?")
    active_contract = fields.Boolean(string="Contrato Ativo?", copy=False)

    payment_mode_id = fields.Many2one(
        'payment.mode', string=u"Modo de pagamento")
    invoice_period = fields.Selection(
        [('1', 'Mensal'), ('6', 'Semestral'), ('12', 'Anual')],
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
    is_contract = fields.Boolean("Apenas Contrato")

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['payment_mode_id'] = self.payment_mode_id.id
        res['date_invoice'] = self.next_invoice
        return res

    @api.onchange('order_line')
    def _onchange_product_id(self):
        if filter(lambda item: item.recurring_line, self.order_line):
            self.recurring_contract = True

    @api.onchange('active_contract', 'invoice_period', 'payment_term_id')
    def _onchange_active_contract(self):
        if self.active_contract and self.invoice_period:
            if self.payment_term_id.indPag == '3':
                add = relativedelta(months=int(self.invoice_period))
                inv_day = self.payment_term_id.invoice_day
                start_date = parser.parse((self.start_contract))
                self.next_invoice = start_date.replace(day=inv_day) + add
            else:
                raise UserError("Condição de Pagamento Inválida")
        if not self.active_contract:
            self.next_invoice = False

    def _create_contract(self):
        new_order = self.copy({
            'origin': self.name,
            'client_order_ref': 'Contrato ' + self.name,
            'is_contract': True,
        })
        non_recurrent_lines = filter(lambda line: not line.recurring_line,
                                     new_order.order_line)
        map(lambda line: line.unlink(), non_recurrent_lines)

        return new_order

    @api.multi
    def action_confirm(self):
        '''
            Verifica se possui venda de produto recorrente. Caso possua somente
            produtos com recorrenciavserá apenas marcado como "is_contract",
            caso tenha produtos mistos será duplica a cotação separando os
            produtos com recorrência.
        '''
        res = super(SaleOrder, self).action_confirm()
        recurrent_lines = map(
            lambda line: line.recurring_line, self.order_line)
        contract_id = self
        if recurrent_lines and False in recurrent_lines:
            contract_id = self._create_contract()

        pgto = self.env['account.payment.term']
        payment_term_id = pgto.search([('indPag', '=', '3')], limit=1)
        contract_id.write({
            'is_contract': True,
            'payment_term_id': payment_term_id.id or False
        })
        return res

    @api.multi
    def action_invoice_contracts(self):
        sale_orders = self.search([('active_contract', '=', True),
                                   ('next_invoice', '<=', date.today()),
                                   ('state', 'in', ('sale', 'done'))])
        for order in sale_orders:
            end_contract = fields.Date.from_string(order.end_contract)
            if end_contract < date.today():  # Cancelar contrato
                order.active_contract = False
                order.next_invoice = False
                continue

            last_invoice = fields.Date.from_string(order.next_invoice)
            order.action_invoice_create(final=True)
            order.next_invoice = last_invoice + relativedelta(
                months=1, day=last_invoice.day)

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

    recurring_line = fields.Boolean(
        string="Recorrente?", related="product_id.recurring_product",
        readonly=True)

    @api.depends('product_id', 'purchase_price', 'product_uom_qty',
                 'price_unit', 'discount')
    def _product_margin(self):
        return super(SaleOrderLine, self)._product_margin()

    @api.depends('qty_invoiced', 'qty_delivered',
                 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        super(SaleOrderLine, self)._get_to_invoice_qty()

        for line in self:
            if line.order_id.state in ['sale', 'done'] and \
               line.order_id.recurring_contract:

                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty

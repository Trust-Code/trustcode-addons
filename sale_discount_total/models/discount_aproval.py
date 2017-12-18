# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleDiscount(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        [('draft', 'Cotação'),
         ('sent', 'Cotação Enviada'),
         ('waiting', 'Aguardando Aprovação'),
         ('sale', 'Ordem de Venda'),
         ('done', 'Trancado'),
         ('cancel', 'Cancelado')],
        string='Status',
        readonly=True,
        copy=False,
        index=True,
        track_visibility='onchange',
        default='draft')

    @api.multi
    def action_confirm(self):
        discnt = 0.0
        no_line = 0.0
        for order in self:
            if order.company_id.discount_approval:
                for line in order.order_line:
                    no_line += 1
                    discnt += line.discount
                discnt = (discnt / no_line)
                if (order.company_id.limit_discount and discnt >
                        order.company_id.limit_discount):
                    order.state = 'waiting'
                    return True
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()
        if self.env['ir.config_parameter'].sudo().get_param(
                'sale.auto_done_setting'):
            self.action_done()
        return True

    @api.multi
    def action_approve(self):
        for order in self:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            # order.order_line._action_procurement_create()
        if self.env['ir.config_parameter'].sudo().get_param(
                'sale.auto_done_setting'):
            self.action_done()
        return True


class ResCompany(models.Model):
    _inherit = 'res.company'

    limit_discount = fields.Float(
        string="Limite para aprovação",
        help="Desconto a partir do qual é necessário aprovação da venda.")

    discount_approval = fields.Boolean(
        string="Forçar verificação em duas etapas",
        help='Verificar vendas cujo desconto ultrapassa o limite.')

    @api.multi
    def set_default_discount(self):
        if (self.discount_approval and self.discount_approval !=
                self.company_id.discount_approval):
            self.company_id.write({'discount_approval':
                                  self.discount_approval})
        if (self.limit_discount and self.limit_discount !=
                self.company_id.limit_discount):
            self.company_id.write({'limit_discount': self.limit_discount})


class AccountDiscountSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    limit_discount = fields.Float(
        string="Limite para aprovação",
        related='company_id.limit_discount',
        help="Desconto a partir do qual é necessário aprovação da venda.")

    discount_approval = fields.Boolean(
        string="Forçar verificação em duas etapas",
        related='company_id.discount_approval',
        help='Verificar vendas cujo desconto ultrapassa o limite.')

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            company = self.company_id
            self.discount_approval = company.discount_approval
            self.limit_discount = company.limit_discount

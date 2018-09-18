# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def validate_quotations(self):
        not_possible = u'Não é possível agrupar cotações'
        if len(self) < 2:
            raise UserError(u"Selecione mais de uma cotação para ser agrupada")

        if any(item.state not in ('draft', 'sent') for item in self):
            raise UserError(u"Você só pode agrupar cotações no estado 'Cotação'\
e 'Cotação enviada'")

        if any(item.company_id != self[0].company_id for item in self):
            raise UserError(u'{} de empresas diferentes'.format(not_possible))

        if any(item.partner_id != self[0].partner_id for item in self):
            raise UserError(u'{} de parceiros diferentes'.format(not_possible))

        if any(item.fiscal_position_id != self[0].fiscal_position_id for item
               in self):
            raise UserError(u'{} de posicoes fiscais diferentes'.format(
                not_possible))

        if any(sorted(item.agent_ids.ids) != sorted(
                self[0].agent_ids.ids) for item in self):
            raise UserError(u'{} de representantes diferentes'.format(
                not_possible))

    def find_base_line(self, line):
        base_line = self.order_line.filtered(
            lambda x: x.product_id == line.product_id and x.price_unit ==
            line.price_unit and x.discount == line.discount)
        if len(base_line) > 1:
            return base_line[0]
        return base_line

    @api.multi
    def group_orders(self):

        self.validate_quotations()

        first_quotation = self[0]

        for rec in self[1:]:
            for line in rec.order_line:
                base_line = first_quotation.find_base_line()
                if base_line:
                    base_line.product_uom_qty += line.product_uom_qty
                else:
                    line.copy({'order_id': first_quotation.id})
            rec.action_cancel()
            rec.message_post(body=u'Esta cotação foi agrupada em {}'.format(
                first_quotation.name))
        first_quotation.message_post(body=u'Esta cotação agrupou as cotações {}\
'.format(', '.join(self[1:].mapped(lambda x: x.name))))

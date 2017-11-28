# -*- coding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    update_option_recurrent_revenue = fields.Selection([
        ('1', u'Substituir'),
        ('2', u'Somar'),
        ('3', u'Não modificar')],
        string=u'Atual. Oportunidade',
        help=u"1 - Substitui o valor da oportunidade com o valor total desta "
        u"cotação \n 2 - Soma os valores de todas as cotações vinculadas "
        u"a oportunidade e sobrescreve o valor da mesma \n 3 - Não modifica "
        u"o valor da oportunidade",)

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if self.update_option_recurrent_revenue == '1':
            for item in self:
                item.opportunity_id.planned_revenue = item.total_non_recurrent
                item.opportunity_id.recurrent_revenue = item.total_recurrent
        elif self.update_option_recurrent_revenue == '2':
            cotacoes = self.search([
                ('opportunity_id', '=', self.opportunity_id.id)])

            opportunity = 0
            total_recurrent = 0
            total_non_recurrent = 0
            for item in cotacoes:
                opportunity = item.opportunity_id
                total_recurrent += item.total_recurrent
                total_non_recurrent += item.total_non_recurrent
            if opportunity:
                opportunity.planned_revenue = total_non_recurrent
                opportunity.recurrent_revenue = total_recurrent
        return res

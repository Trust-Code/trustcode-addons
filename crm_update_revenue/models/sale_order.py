# -*- coding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    update_option_recurrent_revenue = fields.Selection([
        ('1', 'Substituir'),
        ('2', 'Somar'),
        ('3', 'Não modificar')],
        string='Receita Recorrente',
        help="1 - Substitui o valor da oportunidade com o valor total desta "
        "cotação \n 2 - Soma os valores de todas as cotações vinculadas "
        "a oportunidade e sobrescreve o valor da mesma \n 3 - Não modifica "
        "o valor da oportunidade")

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)

        if self.update_option_recurrent_revenue == '1':
            for item in self:
                item.opportunity_id.recurrent_revenue = item.amount_total
        elif self.update_option_receita_recorrente == '2':
            cotacoes = self.search([
                ('opportunity_id', '=', self.opportunity_id.id)])

            total = 0

            for cotacao in cotacoes:
                total += cotacao.amount_total

            for item in self:
                item.opportunity_id.recurrent_revenue = total

        return res

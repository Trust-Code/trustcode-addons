# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('total_despesas', 'total_seguro', 'product_id',
                  'total_frete', 'total_despesas_aduana')
    def _onchange_frete(self):
        super(PurchaseOrder, self)._onchange_despesas_frete_seguro()
        if self.total_frete == 0 or (
                not self.fiscal_position_id.fiscal_type == 'import'):
            return
        full_weight = self._calc_total_weight()
        res = {}
        sub_frete = self.total_frete
        for line in self.order_line:
            valor_frete = self._calc_percentual_weight(
                line, full_weight)
            line.update({
                'valor_frete': valor_frete
            })
            sub_frete -= round(valor_frete, 2)
            if valor_frete == 0:
                res = {'warning': {
                        'title': _('Warning'),
                        'message': _("O produto %s tem peso igual a zero, \
                            caso não seja alterado, o rateio do frete \
                            não o considerará.") % (line.product_id.name)}}
        self.order_line[0].update(
            {'valor_frete': self.order_line[0].valor_frete + sub_frete})
        if 'warning' in res:
            return res

    def _calc_percentual_weight(self, line, full_weight):
            if line.product_id.fiscal_type == 'service':
                return
            total_weight = (line.product_id.weight * line.product_qty)
            percentual = total_weight / full_weight
            return self.total_frete * percentual

    def _calc_total_weight(self):
        full_weight = 0
        for line in self.order_line:
            if line.product_id.fiscal_type == 'product':
                full_weight += (line.product_id.weight * line.product_qty)
        if full_weight == 0 and self.order_line:
            raise UserError(_("Nenhum dos produtos possui peso cadastrado. \
                    É necessário corrigir para o calculo do frete."))
        return full_weight

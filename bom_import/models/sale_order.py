# © 2018 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    mrp_bom_id = fields.Many2one('mrp.bom', string="Lista de Materiais")

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        vals = super(SaleOrderLine, self)._prepare_procurement_values(
            group_id=group_id)
        if self.mrp_bom_id:
            vals['bom_id'] = self.mrp_bom_id.id
        return vals

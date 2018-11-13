# © 2018, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    commitment_date = fields.Datetime(track_visibility='onchange')
    requisition_date = fields.Datetime(track_visibility='onchange')
    observation_sale_order = fields.Text(
        'Observation', track_visibility='onchange')

    sale_id = fields.Integer(compute="_compute_sale_id", stored=True)

    @api.multi
    def _compute_sale_id(self):
        for inv in self:
            inv.sale_id = self.env['sale.order'].search([
                ('invoice_ids', 'in', inv.id), ('name', '=', inv.origin)])

    @api.multi
    def action_update_observation(self):
        if not self.sale_id:
            raise UserError(_(u'Ordem de venda não definida. Não foi possivel \
editar a observação'))
        return {
            'name': 'Update Observation',
            'type': 'ir.actions.act_window',
            'res_model': 'update.observation.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.sale_id,
                'old_observation': self.observation_sale_order,
            }
        }

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class HelpdeskTicket(models.Model):
    _inherit = ['helpdesk.ticket']

    estrategia = fields.Selection(
        [('nao_atender', 'Não atender'),('atender', 'Atender')],
        string='Estratégia',
        default='atender',
        required=False
        )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email
            self.estrategia = self.partner_id.estrategia
            if self.estrategia == 'nao_atender':
                raise UserError('Você não pode atender este cliente. Consultar responsável')
    
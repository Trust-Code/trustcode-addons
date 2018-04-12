# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models, api


class AccountPaymentConfig(models.TransientModel):
    _inherit = 'account.config.settings'

    debit_note_sequence_id = fields.Many2one(
        'ir.sequence',
        'Sequência da Nota de débito',
        help="Selecione a sequência que será utilizada para \
a nota de débito.")

    @api.model
    def get_default_debit_note_sequence_id(self, fields):
        return {'debit_note_sequence_id':
                self.env.user.company_id.debit_note_sequence_id.id}

    @api.multi
    def set_default_debit_note_sequence_id(self):
        self.env.user.company_id.debit_note_sequence_id\
          = self.debit_note_sequence_id.id

# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    debit_document_id = fields.Many2one(
        'br_account.fiscal.document', string="Documento de Débito")
    debit_note_sequence_id = fields.Many2one(
        'ir.sequence',
        'Sequência da Nota de débito',
        help="Selecione a sequência que será utilizada para a nota de débito.")

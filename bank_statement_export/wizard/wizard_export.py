# © 2019 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import csv
import base64
from io import StringIO
from odoo import api, fields, models


class WizardExportBankTransactions(models.TransientModel):
    _name = 'wizard.export.bank.transaction'

    start_date = fields.Date(string="Data Inicial", required=True)
    end_date = fields.Date(string="Data Final", required=True)
    journal_ids = fields.Many2many('account.journal', string="Diários")
    zip_file = fields.Binary('Arquivo', readonly=True)
    zip_file_name = fields.Char('Nome', size=255)
    state = fields.Selection(
        [('init', 'init'), ('done', 'done')],
        'state', readonly=True, default='init')

    @api.multi
    def action_export_transactions(self):
        domain = [
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
            ('state', '=', 'posted'),
            ('journal_id.type', '=', 'bank'),
        ]
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        moves = self.env['account.move'].search(domain, order='journal_id, date asc')

        output = StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL, delimiter=';')
        writer.writerow([
            'Diário', 'Data Movimento', 'Valor Recebido', 'Valor Pago',
            'Saldo', 'Parceiro', 'Referência',
        ])
        total = 0
        for move in moves:
            debit_id = move.line_ids.filtered(
                lambda x: x.account_id == move.journal_id.default_debit_account_id)
            credit_id = move.line_ids.filtered(
                lambda x: x.account_id == move.journal_id.default_credit_account_id)

            line = [
                move.journal_id.name,
                fields.Date.from_string(move.date).strftime('%d-%m-%Y'),
                debit_id[0].debit or 0.0,
                credit_id[0].credit or 0.0,
                "%.2f" % total,
                move.partner_id.name,
                move.ref,
            ]
            total += round(((debit_id[0].debit or 0.0) or
                           (credit_id[0].credit or 0.0)), 2)
            writer.writerow(line)

        self.zip_file = base64.encodestring(output.getvalue().encode('utf-8'))
        self.zip_file_name = "extrato.csv"

        self.state = 'done'

        mod_obj = self.env['ir.model.data'].search(
            [('model', '=', 'ir.ui.view'),
             ('name', '=', 'view_export_bank_transaction_form')])

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(mod_obj.res_id, 'form')],
            'target': 'new',
        }

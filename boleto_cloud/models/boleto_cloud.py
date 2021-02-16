from datetime import datetime
from odoo import fields, models


class BoletoCloud(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(selection_add=[("boleto.cloud", "Boleto Cloud")])


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    boleto_pdf = fields.Binary(string="Boleto PDF")


class CnabRemessa(models.Model):
    _name = 'cnab.remessa'
    _description = "Remessa de CNAB"
    _order = 'id desc'

    name = fields.Char(max_length=30, string="Nome", required=True, default='/')
    company_id = fields.Many2one('res.company', string='Company')
    user_id = fields.Many2one('res.users', string='Responsável')
    journal_id = fields.Many2one('account.journal', string="Diário")

    cnab_file = fields.Binary('CNAB File', readonly=True)
    data_emissao_cnab = fields.Datetime('Data de Emissão do CNAB')

    def action_get_remessa(self):

        # TODO Conectar na API e pegar o arquivo de remessa
        url = "api/v1/arquivos/cnab/remessas"

        arquivo = None

        remessa = self.write({
            'cnab_file': arquivo,
            'data_emissao_cnab': datetime.now(),
        })
        return remessa


class WizardImportCnabRetorno(models.TransientModel):
    _name = 'wizard.import.cnab.retorno'

    cnab_file = fields.Binary('Arquivo CNAB')


    def action_import_cnab_file(self):
        url = "api/v1/arquivos/cnab/remessas"
        # TODO CHAMAR A API

        statement = self.env['account.bank.statement'].create({
            'name': '',
            'journal_id': '',
            'date': datetime.now().date(),
            'balance_start_real': 0.0,
            'balance_end_real': 0.0,
        })

        for titulo in response['arquivo']['titulos']:

            self.env['account.bank.statement.line'].create({
                'bank_statement_id': statement.id,
                'date': None,
                'name': '',
                'partner_id': None,  # achar a linha original,
                'ref': None,
                'amount': 0.0,
            })


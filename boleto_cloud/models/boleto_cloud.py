import requests
import base64
from datetime import datetime
from odoo import fields, models
from odoo.exceptions import UserError


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
        acquirer = self.env['payment.acquirer'].search([('provider', '=', 'boleto.cloud')])
        if acquirer.state == 'enabled':
            url = 'https://app.boletocloud.com/api/v1/arquivos/cnab/remessas'
        else:
            url = 'https://sandbox.boletocloud.com/api/v1/arquivos/cnab/remessas'
        api_token = self.company_id.boleto_cloud_api_token
        data = {
            'boleto.conta.token': self.payment_journal_id.boleto_cloud_bank_account_api_key,
        }
        response = requests.post(url, data=data, auth=(api_token, 'token'))

        if response.status_code == '204':
            raise UserError('Não há remessas CNAB a serem geradas.')
        elif response.status_code == '201':
            arquivo = base64.b64encode(response.content)
            remessa = self.write({
                'cnab_file': arquivo,
                'data_emissao_cnab': datetime.now(),
            })
        else:
            jsonp = response.json()
            message = '\n'.join([x['mensagem'] for x in jsonp['erro']['causas']])
            raise UserError('Houve um erro com a API do Boleto Cloud:\n%s' % message)
        return remessa


class WizardImportCnabRetorno(models.TransientModel):
    _name = 'wizard.import.cnab.retorno'

    cnab_file = fields.Binary('Arquivo CNAB')
    journal_id = fields.Many2one('account.journal', string='Diário')

    def action_import_cnab_file(self):
        if not self.cnab_file:
            raise UserError('Arquivo CNAB não definido.')
        if not (self.journal_id or self.journal_id.use_boleto_cloud):
            raise UserError('Diário não definido ou não configurado para usar o Boleto Cloud.')

        acquirer = self.env['payment.acquirer'].search([('provider', '=', 'boleto.cloud')])
        if acquirer.state == 'enabled':
            url = 'https://app.boletocloud.com/api/v1/arquivos/cnab/retornos'
        else:
            url = 'https://sandbox.boletocloud.com/api/v1/arquivos/cnab/retornos'
        api_token = self.company_id.boleto_cloud_api_token

        response = requests.post(url, files=self.cnab_file, auth=(api_token, 'token'))
        last_statement = self.env['account.bank.statement'].search([], order='id_desc', limit=1)

        statement = self.env['account.bank.statement'].create({
            'name': response['arquivo']['protocolo']['numero'],
            'journal_id': self.journal_id.id,
            'date': datetime.now().date(),
            'balance_start_real': last_statement.balance_end_real,
            'balance_end_real': last_statement.balance_end_real + last_statement.total_entry_encoding,
        })

        for titulo in response['arquivo']['titulos']:
            transaction = self.env['payment.transaction'].search([('acquirer_reference', '=', titulo['token'])])
            self.env['account.bank.statement.line'].create({
                'bank_statement_id': statement.id,
                'date': datetime.strptime(titulo['vencimento'], '%Y-%m-%d'),
                'name': titulo['numero'],
                'partner_id': transaction.partner_id.id,
                'ref': titulo['token'],
                'amount': 0.0,
            })

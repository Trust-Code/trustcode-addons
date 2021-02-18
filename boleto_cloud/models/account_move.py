import re
import base64
import requests
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    boleto_pdf = fields.Binary()
    

class AccountMove(models.Model):
    _inherit = 'account.move'

    def validate_data_boleto(self):
        errors = []
        for invoice in self:
            if not invoice.payment_journal_id.use_boleto_cloud:
                continue
            partner = invoice.partner_id.commercial_partner_id
            if not self.env.company.boleto_cloud_api_token:
                errors.append('Configure o token de API Boledo Cloud')
            if partner.is_company and not partner.l10n_br_legal_name:
                errors.append('Destinatário - Razão Social')
            if not partner.street:
                errors.append('Destinatário / Endereço - Rua')
            if not partner.l10n_br_number:
                errors.append('Destinatário / Endereço - Número')
            if not partner.zip or len(re.sub(r"\D", "", partner.zip)) != 8:
                errors.append('Destinatário / Endereço - CEP')
            if not partner.state_id:
                errors.append(u'Destinatário / Endereço - Estado')
            if not partner.city_id:
                errors.append(u'Destinatário / Endereço - Município')
            if not partner.country_id:
                errors.append(u'Destinatário / Endereço - País')
        if len(errors) > 0:
            msg = "\n".join(
                ["Por favor corrija os erros antes de prosseguir"] + errors)
            raise ValidationError(msg)

    def send_information_to_boleto_cloud(self):
        if not self.payment_journal_id.use_boleto_cloud or not \
                self.payment_journal_id.boleto_cloud_bank_account_api_key:
            return

        # base_url = (
        #     self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        # )

        for moveline in self.receivable_move_line_ids:
            acquirer = self.env['payment.acquirer'].search([('provider', '=', 'boleto.cloud')])
            if not acquirer:
                raise UserError('Configure o modo de pagamento do boleto cloud')
            transaction = self.env['payment.transaction'].create({
                'acquirer_id': acquirer.id,
                'amount': moveline.amount_residual,
                'currency_id': moveline.move_id.currency_id.id,
                'partner_id': moveline.partner_id.id,
                'type': 'server2server',
                'date_maturity': moveline.date_maturity,
                'invoice_ids': [(6, 0, self.ids)],
            })

            if acquirer.state == 'enabled':
                url = 'https://app.boletocloud.com'
            else:
                url = 'https://sandbox.boletocloud.com'

            api_token = self.company_id.boleto_cloud_api_token

            instrucao = self.payment_journal_id.instrucoes or ''
            instrucoes = [instrucao[y-95:y] for y in range(95, len(instrucao)+95, 95)]

            vals = {
                'boleto.conta.token': self.payment_journal_id.boleto_cloud_bank_account_api_key,
                'boleto.emissao': self.invoice_date,
                'boleto.vencimento': self.invoice_date_due,
                'boleto.documento': self.name,
                'boleto.titulo': "DM",
                'boleto.valor': "%.2f" % self.amount_total,
                'boleto.pagador.nome': self.partner_id.name,
                'boleto.pagador.cprf': self.partner_id.l10n_br_cnpj_cpf,
                'boleto.pagador.endereco.cep': "%s-%s" % (self.partner_id.zip[:5], self.partner_id.zip[-3:]),
                'boleto.pagador.endereco.uf': self.partner_id.state_id.code,
                'boleto.pagador.endereco.localidade': self.partner_id.city_id.name,
                'boleto.pagador.endereco.bairro': self.partner_id.l10n_br_district,
                'boleto.pagador.endereco.logradouro': self.partner_id.street,
                'boleto.pagador.endereco.numero': self.partner_id.l10n_br_number,
                'boleto.pagador.endereco.complemento': "",
                'boleto.instrucao': instrucoes[:8],
            }

            response = requests.post("%s/api/v1/boletos" % url, data=vals, auth=(api_token, 'token'))
            if response.status_code == 201:
                boleto_pdf = base64.b64encode(response.content)

                boleto_id = response.headers['X-BoletoCloud-Token']
                boleto_numero = response.headers['X-BoletoCloud-NIB-Nosso-Numero']

            elif response.status_code == 409:
                transaction = self.env['payment.transaction'].search([
                    ('acquirer_id', '=', acquirer.id),
                    ('amount', '=', moveline.amount_residual),
                    ('currency_id', '=', moveline.move_id.currency_id.id),
                    ('partner_id', '=', moveline.partner_id.id),
                    ('invoice_ids', '=', self.ids)], limit=1)

                url = "%s/api/v1/boletos" % url + transaction.acquirer_reference
                response = requests.get(url, auth=(api_token, 'token'))
                boleto_pdf = base64.b64encode(response.content)
                boleto_id = transaction.acquirer_reference
            else:
                jsonp = response.json()
                message = '\n'.join([x['mensagem'] for x in jsonp['erro']['causas']])
                raise UserError('Houve um erro com a API do Boleto Cloud:\n%s' % message)

            transaction.write({
                'acquirer_reference': boleto_id,
                'transaction_url': "%s/boleto/2via/%s" % (url, boleto_id),
                'boleto_pdf': boleto_pdf,
            })

    def generate_boleto_cloud_transactions(self):
        for item in self:
            item.send_information_to_boleto_cloud()

    def action_post(self):
        self.validate_data_boleto()
        result = super(AccountMove, self).action_post()
        self.generate_boleto_cloud_transactions()
        return result

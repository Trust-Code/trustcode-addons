import re
import base64
import requests
from odoo import api, fields, models
from odoo.exceptions import ValidationError



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

        base_url = (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )

        for moveline in self.receivable_move_line_ids:

            # acquirer = self.env['payment.acquirer'].search([('provider', '=', 'boleto.cloud')])
            # transaction = self.env['payment.transaction'].create({
            #     'acquirer_id': acquirer.id,
            #     'amount': moveline.amount_residual,
            #     'currency_id': moveline.move_id.currency_id.id,
            #     'partner_id': moveline.partner_id.id,
            #     'type': 'server2server',
            #     'date_maturity': moveline.date_maturity,
            #     'origin_move_line_id': moveline.id,
            #     'invoice_ids': [(6, 0, self.ids)]
            # })

            url = 'https://sandbox.boletocloud.com/api/v1/boletos'

            api_token = self.company_id.boleto_cloud_api_token
            import ipdb
            ipdb.set_trace()
            vals = {
                'boleto.conta.token': self.payment_journal_id.boleto_cloud_bank_account_api_key,
                'boleto.emissao': self.invoice_date,
                'boleto.vencimento': self.invoice_date_due,
                'boleto.documento': self.name,
                'boleto.titulo': self.name,
                'boleto.valor': self.amount_total,
                'boleto.pagador.nome': self.partner_id.name,
                'boleto.pagador.cprf': self.partner_id.l10n_br_cnpj_cpf,
                'boleto.pagador.endereco.cep': self.partner_id.zip,
                'boleto.pagador.endereco.uf': self.partner_id.state_id.code,
                'boleto.pagador.endereco.localidade': self.partner_id.city_id.name,
                'boleto.pagador.endereco.bairro': self.partner_id.l10n_br_district,
                'boleto.pagador.endereco.logradouro': self.partner_id.street,
                'boleto.pagador.endereco.numero': self.partner_id.l10n_br_number,
                'boleto.pagador.endereco.complemento': "Sítio - Subindo a serra da Mantiqueira",
                'boleto.instrucao': "Atenção! NÃO RECEBER ESTE BOLETO.",
                'boleto.instrucao': "Este é apenas um teste utilizando a API Boleto Cloud",
                'boleto.instrucao': "Mais info em http://boleto"
            }

            
            response = requests.post(url, data=vals, auth=(api_token, 'token'))
            
            if response.status_code == 201:
                
                moveline.boleto_pdf = base64.b64encode(response.text.encode('utf-8'))
                

                boleto_id = response.headers['X-BoletoCloud-Token']
                boleto_url = response.headers['Location']
                boleto_numero = response.headers['X-BoletoCloud-NIB-Nosso-Numero']
            
            elif response.status_code == 409:
                # ja foi criado previamente
                # buscar o que ja foi emitido
                pass


            # print(response.text)

            # transaction.write({
            #     'acquirer_reference': data['id'],
            #     'transaction_url': data['secure_url'],
            # })


    def generate_boleto_cloud_transactions(self):
        for item in self:
            item.send_information_to_boleto_cloud()

    def action_post(self):
        self.validate_data_boleto()
        result = super(AccountMove, self).action_post()
        self.generate_boleto_cloud_transactions()
        return result

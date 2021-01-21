# © 2020 Danimar Ribeiro, Trustcode
# Part of Trustcode. See LICENSE file for full copyright and licensing details.

import re
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import date
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def validate_data_for_payment_gateway(self):
        errors = []
        for invoice in self:
            if not invoice.payment_journal_id.payment_acquirer_id:
                continue
            partner = invoice.partner_id.commercial_partner_id
            acquirer = invoice.payment_journal_id.payment_acquirer_id
            if not acquirer.zoop_api_key:
                errors.append('Configure o token de API do Zoop')
            if not acquirer.zoop_marketplace_id:
                errors.append('Configure o codigo odo marketplace do Zoop')
            if not acquirer.zoop_seller_id:
                errors.append('Configure o codigo de vendedor do Zoop')
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

    def send_information_to_zoop(self):
        if not self.payment_journal_id.payment_acquirer_id:
            return

        acquirer = self.payment_journal_id.payment_acquirer_id
        self.partner_id.action_synchronize_with_zoop(acquirer)

        for moveline in self.receivable_move_line_ids:

            transaction = self.env['payment.transaction'].create({
                'acquirer_id': acquirer.id,
                'amount': moveline.amount_residual,
                'currency_id': moveline.move_id.currency_id.id,
                'partner_id': moveline.partner_id.id,
                'type': 'server2server',
                'date_maturity': moveline.date_maturity,
                'origin_move_line_id': moveline.id,
                'invoice_ids': [(6, 0, self.ids)]
            })

            installment = {
                "mode": "interest_free",
                "number_installments": 1,
            }
            payment_method = {
                "expiration_date": moveline.date_maturity.isoformat(),
                "top_instructions": [],
            }
            invoice_data = {
                "amount": int(moveline.amount_residual * 100),
                "currency": "BRL",
                "description": 'Fatura Ref: %s' % self.name,
                "payment_type": "boleto",
                "reference_id": transaction.reference,
                "payment_method": payment_method,
                "installment_plan": installment,
                "on_behalf_of": acquirer.zoop_seller_id,
                "customer": self.partner_id.zoop_sync_id,
            }
            url = "https://api.zoop.ws/v1/marketplaces/%s/transactions" % acquirer.zoop_marketplace_id
            auth = HTTPBasicAuth(acquirer.zoop_api_key, "")
            headers = {
                'content-type': 'application/json',
            }
            payload = json.dumps(invoice_data)
            response = requests.request("POST", url, data=payload, headers=headers, auth=auth)
            if response.status_code == 200:
                json_resp = response.json()
                raise UserError(json_resp['error']['message'])
            elif response.status_code in (401, 403, 405):
                raise UserError("Configure corretamente as credenciais do Zoop")
            if response.status_code != 201:
                raise UserError("Erro ao se conectar com o Zoop: %s".format(response.message()))

            data = response.json()
            transaction.write({
                'acquirer_reference': data['id'],
                'transaction_url': data["payment_method"]["url"],
            })

    def generate_transaction_for_zoop(self):
        for item in self:
            item.send_information_to_zoop()

    def action_post(self):
        self.validate_data_for_payment_gateway()
        result = super(AccountMove, self).action_post()
        self.generate_transaction_for_zoop()
        return result


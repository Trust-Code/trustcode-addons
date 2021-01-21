# © 2020 Danimar Ribeiro, Trustcode
# Part of Trustcode. See LICENSE file for full copyright and licensing details.

import re
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from werkzeug import urls


class ZoopBoleto(models.Model):
    _inherit = "payment.acquirer"

    def _default_return_url(self):
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        return "%s%s" % (base_url, "/payment/process")

    provider = fields.Selection(selection_add=[("zoop", "Zoop")])
    zoop_api_key = fields.Char("Zoop Api Key")
    zoop_marketplace_id = fields.Char("Zoop Marketplace ID")
    zoop_seller_id = fields.Char("Zoop ID Vendedor")

    def zoop_form_generate_values(self, values):
        """ Função para gerar HTML POST do PagHiper """
        base_url = (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        partner_id = values.get('billing_partner')
        partner_id.action_synchronize_with_zoop(self)

        installment = {
            "mode": "interest_free",
            "number_installments": 1,
        }
        payment_method = {
            "expiration_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "top_instructions": [],
        }
        invoice_data = {
            "amount": int(values.get('amount') * 100),
            "currency": "BRL",
            "description": 'Fatura Ref: %s' % values.get('reference'),
            "payment_type": "boleto",
            "reference_id": values.get("reference"),
            "payment_method": payment_method,
            "installment_plan": installment,
            "on_behalf_of": self.zoop_seller_id,
            "customer": partner_id.zoop_sync_id,
        }
        url = "https://api.zoop.ws/v1/marketplaces/%s/transactions" % self.zoop_marketplace_id
        auth = HTTPBasicAuth(self.zoop_api_key, "")
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
            raise UserError("Erro ao se conectar com o Zoop")

        result = response.json()
        acquirer_reference = result["id"]
        payment_transaction_id = self.env['payment.transaction'].search(
            [("reference", "=", values['reference'])])

        payment_transaction_id.write({
            "acquirer_reference": acquirer_reference,
            "invoice_url": result["payment_method"]["url"],
        })
        return {
            "checkout_url": urls.url_join(
                base_url, "/zoop/checkout/redirect"),
            "secure_url": result["payment_method"]["url"]
        }


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    invoice_url = fields.Char(string="Fatura", size=300)

    @api.model
    def _zoop_form_get_tx_from_data(self, data):
        acquirer_reference = data.get("data[id]")
        tx = self.search([("acquirer_reference", "=", acquirer_reference)])
        return tx[0]

    def _zoop_form_validate(self, data):
        status = data.get("data[status]")

        if status in ('paid', 'partially_paid', 'authorized'):
            self._set_transaction_done()
            return True
        elif status == 'pending':
            self._set_transaction_pending()
            return True
        else:
            self._set_transaction_cancel()
            return False

    def action_verify_transaction(self):
        super(PaymentTransaction, self).action_verify_transaction()
        if self.acquirer_id.provider != 'zoop':
            return
        url = "https://api.zoop.ws/v1/marketplaces/%s/transactions/%s" % (
            self.acquirer_id.zoop_marketplace_id, self.acquirer_reference)
        auth = HTTPBasicAuth(self.acquirer_id.zoop_api_key, "")
        headers = {
            'content-type': 'application/json',
        }
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "succeeded" and self.state not in ('done', 'authorized'):
            self._set_transaction_done()
            self._post_process_after_done()
            if self.origin_move_line_id:
                self.origin_move_line_id._create_bank_tax_move(data.get('fees') or 0)

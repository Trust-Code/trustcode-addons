# © 2020 Danimar Ribeiro, Trustcode
# Part of Trustcode. See LICENSE file for full copyright and licensing details.

import re
import json
import requests
from requests.auth import HTTPBasicAuth
from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    zoop_sync_id = fields.Char(string="ID Zoop", size=100)

    def action_synchronize_with_zoop(self, payment_acquirer):
        for partner in self:
            if partner.zoop_sync_id:
                continue

            commercial_part = partner.commercial_partner_id
            complete_name = commercial_part.l10n_br_legal_name or commercial_part.name
            name, *surname = complete_name.split(' ', 1)
            vals = {
                'email': partner.email,
                'first_name': name,
                'last_name': surname[0] if surname else '',
                'taxpayer_id': commercial_part.l10n_br_cnpj_cpf,
                'address': {
                    'postal_code': re.sub('[^0-9]', '', commercial_part.zip or ''),
                    'line1': commercial_part.street + ' ' + commercial_part.l10n_br_number,
                    'city': commercial_part.city_id.name,
                    'state': commercial_part.state_id.code,
                    'neighborhood': commercial_part.l10n_br_district or '',
                    'line2': commercial_part.street2 or '',
                    'country_code': 'BR',
                },
            }

            url = "https://api.zoop.ws/v1/marketplaces/%s/buyers" % payment_acquirer.zoop_marketplace_id
            auth = HTTPBasicAuth(payment_acquirer.zoop_api_key, "")
            headers = {
                'content-type': 'application/json',
            }
            payload = json.dumps(vals)
            response = requests.request("POST", url, data=payload, headers=headers, auth=auth)
            if response.status_code == 200:
                json_resp = response.json()
                raise UserError(json_resp['error']['message'])
            elif response.status_code in (401, 403, 405):
                raise UserError("Configure corretamente as credenciais do Zoop")
            if response.status_code != 201:
                raise UserError("Erro ao se conectar com o Zoop")

            partner.zoop_sync_id = response.json()['id']


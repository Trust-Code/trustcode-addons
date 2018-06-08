# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests
import json
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    otrs_server = fields.Char('Server OTRS')
    otrs_login = fields.Char('Login OTRS')
    otrs_password = fields.Char('Senha OTRS')

    def otrs_post_method(self, route, method, data):
        headers = {'Content-Type': 'application/json'}
        domain = self.get_otrs_domain(self.company_id.otrs_webservice_domain,
                                      route)
        data = json.dumps(data)
        response = requests.post(domain, headers=headers, data=data)
        self.parse_otrs_response(response)

    def get_otrs_domain(self, domain, route):
        return '{}/{}?UserLogin={}&Password={}'.format(
            domain, route, self.otrs_login, self.otrs_password)

    def parse_otrs_response(self, respose):
        return True

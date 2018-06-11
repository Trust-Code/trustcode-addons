# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests
import json
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    otrs_login = fields.Char('Login OTRS')
    otrs_password = fields.Char('Senha OTRS')

    def otrs_post(self, route, data):
        headers = {'Content-Type': 'application/json'}
        domain = self.get_otrs_domain(
            self.company_id.otrs_domain,
            self.company_id.otrs_webservice_name,
            route)
        data = json.dumps(data)
        return requests.post(url=domain, headers=headers, data=data)

    def otrs_get(self, route, data=None):
        if data:
            data = json.dumps(data)
        return requests.get(url=self.get_otrs_domain(
            self.company_id.otrs_domain,
            self.company_id.otrs_webservice_name,
            route), data=data)

    def otrs_patch(self, route, data):
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(data)
        return requests.patch(url=self.get_otrs_domain(
            self.company_id.otrs_domain,
            self.company_id.otrs_webservice_name,
            route),
            headers=headers, data=data)

    def otrs_search(self, route, data=None):
        if data:
            data = json.dumps(data)
        return requests.get(url=self.get_otrs_domain(
            self.company_id.otrs_domain,
            self.company_id.otrs_webservice_name,
            route),
            data=data)

    def get_otrs_domain(self, domain, webservice, route):
        return '{}/nph-genericinterface.pl/Webservice/{}/{}?UserLogin={}\
&Password={}'.format(domain, webservice, route, self.otrs_login,
                     self.otrs_password)

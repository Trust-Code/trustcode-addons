# -*- encoding: utf-8 -*-
# © 2018 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests
import json
import random
import string
import logging
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def gen_random_string(char_set, length):
    if not hasattr(gen_random_string, "rng"):
        gen_random_string.rng = random.SystemRandom()
    return ''.join([gen_random_string.rng.choice(char_set)
                    for _ in range(length)])


class ResPartner(models.Model):
    _inherit = 'res.partner'

    edx_username = fields.Char('Username in EDX')
    edx_password = fields.Char('Password generated for create EDX user')
    edx_active = fields.Boolean(string="Ativo no EDX")

    def get_username(self):
        return self.email.split('@')[0] + str(self.id)

    def get_base_url(self):
        params = self.env['ir.config_parameter'].sudo()
        return params.get_param(
            'edx_integration.edx_url', default="")

    def get_client_id(self):
        params = self.env['ir.config_parameter'].sudo()
        return params.get_param(
            'edx_integration.edx_client_id', default="")

    def get_client_secret(self):
        params = self.env['ir.config_parameter'].sudo()
        return params.get_param(
            'edx_integration.edx_client_secret', default="")

    def get_user(self):
        token = self.get_token()
        session = requests.Session()
        base_url = self.get_base_url()
        if not self.edx_username:
            username = self.get_username()
        else:
            username = self.edx_username

        url_api = base_url + '/api/user/v1/accounts/' + username

        header = {
            'Content-Type': 'application/merge-patch+json',
            'Authorization': 'JWT ' + token
        }

        request = session.get(url_api, headers=header)

        if request.status_code == 200:
            self.write({
                'edx_username': username,
                'edx_active': request.json().get('is_active')
            })
            return True
        else:
            return False

    def create_edx_user(self):
        base_url = self.get_base_url()
        session = requests.Session()
        password_charset = string.ascii_letters + string.digits
        password = gen_random_string(password_charset, 32)
        username = self.get_username()
        mailing_address = (self.street, ", ", self.street2, ", ",
                           self.number, ", ", self.district, ", ",
                           self.zip)
        payload = {
            'email': self.email,
            'name': self.name,
            'username': username,
            'password': password,
            'mailing_address': mailing_address,
            'city': self.city_id.name,
            'country': self.country_id.code,
            'goals': 'Be the best in Odoo',
            'terms_of_service': 'true',
            'honor_code': 'true'
        }

        url_api = base_url + '//user_api/v1/account/registration/'

        request = session.post(url_api, data=payload)
        if request.status_code != 200:
            raise UserError(
                'Não foi possível registrar o usuário %s %s'
                % (username, request.reason))

        self.write({
            'edx_username': username,
            'edx_password': password,
        })

        self.update_edx_user(True)

    def get_token(self):
        session = requests.Session()
        base_url = self.get_base_url()

        url_api = base_url + '/oauth2/access_token'

        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.get_client_id(),
            'client_secret': self.get_client_secret(),
            'token_type': 'jwt'
        }

        request = session.post(url_api, data=payload)

        if request.status_code == 200:
            return request.json().get('access_token')

        raise(request.text)

    @api.multi
    def update_edx_user(self, active):
        token = self.get_token()
        session = requests.Session()
        username = self.edx_username
        base_url = self.get_base_url()

        header = {
            'Content-Type': 'application/merge-patch+json',
            'Authorization': 'JWT ' + token
        }

        payload = json.dumps({
            'is_active': active,
        })

        url_api = base_url + '/api/user/v1/accounts/' + username
        request = session.patch(url_api, data=payload, headers=header)

        if request.status_code != 200:
            raise UserError('Não foi possível ativar o usuário: %s %s'
                            % (username, request.reason))

        if active:
            self.enrollment(username, self.get_courses())

        self.write({'edx_active': active})

    @api.multi
    def get_courses(self):
        session = requests.Session()
        token = self.get_token()
        base_url = self.get_base_url()

        header = {
            'Authorization': 'JWT ' + token
        }

        url_api = base_url + '/api/courses/v1/courses/'

        request = session.get(url_api, headers=header)

        if request.status_code == 200:
            return request.json()

        raise(request.text)

    @api.multi
    def enrollment(self, username, courses, active=True):
        for course in courses['results']:
            session = requests.Session()
            token = self.get_token()
            base_url = self.get_base_url()

            header = {
                'Authorization': 'JWT ' + token,
                'Content-Type': 'application/json',
            }

            url_api = base_url + '/api/enrollment/v1/enrollment'

            payload = json.dumps({
                'user': username,
                'is_active': active,
                'course_details': {
                    'course_id': course['id']
                }
            })

            request = session.post(url_api, headers=header, data=payload)

            if request.status_code != 200:
                raise UserError(
                    'Não foi possível registrar o usuário:', username,
                    ' no curso:', course)

# -*- encoding: utf-8 -*-
# © 2018 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_in_edx(self):
        import ipdb
        ipdb.set_trace()
        return self.partner_id.edx_active

    def _set_in_edx(self):
        self.partner_id.write({'edx_active': not self.in_edx})

    edx_username = fields.Char('Username in EDX')
    edx_password = fields.Char('Password generated for create EDX user')
    edx_active = fields.Boolean(
        string="Ativo no EDX", compute='_get_in_edx', inverse="_set_in_edx")

    def get_user(self):
        token = self.get_token()
        session = requests.Session()
        username = self.partner_id.edx_username
        url_api = 'http://52.55.244.3:8080/api/user/v1/accounts/' + username

        header = {
            'Content-Type': 'application/merge-patch+json',
            'Authorization': 'JWT ' + token
        }

        url_api = 'http://52.55.244.3:8080//user_api/v1/account/registration/'
        request = session.patch(url_api, headers=header)

        if request.status_code == 200:
            return True
        else:
            return False

    def create_edx_user(self):
        session = requests.Session()
        partner_id = self.partner_id
        username = partner_id.email.split('@')[0] + str(partner_id.id)
        mailing_address = (partner_id.street, ", ", partner_id.street2, ", ",
                           partner_id.number, ", ", partner_id.district, ", ",
                           partner_id.zip)
        payload = {
            'email': partner_id.email,
            'name': partner_id.name,
            'username': username,
            'password': partner_id.edx_password,
            'mailing_address': mailing_address,
            'city': partner_id.city_id.name,
            'country': partner_id.country_id.code,
            'goals': 'Be the best in Odoo',
            'terms_of_service': 'true',
            'honor_code': 'true'
        }

        url_api = 'http://52.55.244.3:8080//user_api/v1/account/registration/'
        # url_api = 'http://104.156.230.114//user_api/v1/account/registration/'

        request = session.post(url_api, data=payload)

        if request != 200:
            raise UserError('Não foi possível registrar o usuário')

        self.partner_id.write({'edx_username': username})
        self.update_edx_user(True)

    def get_token(self):
        session = requests.Session()

        url_api = 'http://52.55.244.3:8080/oauth2/access_token'

        payload = {
            'grant_type': 'client_credentials',
            'client_id': '7f447db1ceffbf04410e',
            'client_secret': 'c288965eefe735fe193932d658c464a426c73ce5',
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
        username = self.partner_id.edx_username

        header = {
            'Content-Type': 'application/merge-patch+json',
            'Authorization': 'JWT ' + token
        }

        payload = json.dumps({
            'is_active': active,
        })

        url_api = 'http://52.55.244.3:8080/api/user/v1/accounts/' + username
        request = session.patch(url_api, data=payload, headers=header)

        if request.status_code != 200:
            raise UserError('Não foi possível ativar o usuário: ', username)

        self.enrollment(username, self.get_courses())

    @api.multi
    def get_courses(self):
        session = requests.Session()
        token = self.get_token()

        header = {
            'Authorization': 'JWT ' + token
        }

        url_api = 'http://52.55.244.3:8080/api/courses/v1/courses/'

        request = session.post(url_api, headers=header)

        if request.status_code == 200:
            return request.json()

        raise(request.text)

    @api.multi
    def enrollment(self, username, courses, active=True):
        for course in courses:
            session = requests.Session()
            token = self.get_token()

            header = {
                'Authorization': 'JWT ' + token
            }

            url_api = 'http://52.55.244.3:8080/api/enrollment/v1/enrollment'

            payload = {
                'user': username,
                'is_active': active,
                'course_details': {
                    'course_id': course
                }
            }

            request = session.post(url_api, headers=header, data=payload)

            if request.status_code != 200:
                raise UserError(
                    'Não foi possível registrar o usuário:', username,
                    ' no curso:', course)

    @api.multi
    def action_apply(self):
        import ipdb
        ipdb.set_trace()
        self.env['res.partner'].check_access_rights('write')

        error_msg = self.get_error_messages()
        if error_msg:
            raise UserError("\n\n".join(error_msg))

        for wizard_user in self.sudo().with_context(active_test=False):
            if wizard_user.in_edx:
                if not self.get_user():
                    password_charset = string.ascii_letters + string.digits
                    password = gen_random_string(password_charset, 32)
                    username = (self.partner_id.email.split('@')[0] +
                                str(self.partner_id.id))
                    self.partner_id.write({
                        'edx_username': username,
                        'edx_password': password,
                        'edx_active': True
                    })
                    wizard_user.with_context(active_test=True)._send_email()
                    wizard_user.create_edx_user()
                else:
                    wizard_user.update_edx_user(True)
                wizard_user.refresh()
            else:
                self.partner_id.write({
                    'edx_active': True,
                })
                wizard_user.update_edx_user(False)

    @api.multi
    def _send_email(self):
        """ send notification email to a new edx user """
        if not self.env.user.email:
            raise UserError(_(
                'You must have an email address in your' +
                ' User Preferences to send emails.'))

        # determine subject and body in the edx user's language
        template = self.env.ref(
            'edx_integration.mail_template_data_edx_welcome')
        for wizard_line in self:
            lang = wizard_line.partner_id.lang
            partner = wizard_line.partner_id

            edx_url = partner.with_context(
                signup_force_type_in_url='',
                lang=lang)._get_signup_url_for_action()[partner.id]
            partner.signup_prepare()

            if template:
                template.with_context(
                    dbname=self._cr.dbname, edx_url=edx_url,
                    lang=lang).send_mail(wizard_line.id, force_send=True)
            else:
                _logger.warning(
                    "No email template found for sending" +
                    " email to the edx user")

        return True

# -*- coding: utf-8 -*-
# © 2018 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools import email_split

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''


class EdxWizard(models.TransientModel):
    """
        A wizard to manage the creation/removal of EDX users.
    """

    _name = 'edx.wizard'
    _description = 'EDX Access Management'

    user_ids = fields.One2many('edx.wizard.user', 'wizard_id', string='Users')
    welcome_message = fields.Text(
        'Invitation Message',
        help="This text is included in the email sent" +
        " to new users of the edx.")

    @api.onchange('welcome_message')
    def onchange_welcome_message(self):
        partner_ids = self.env.context.get('active_ids', [])
        contact_ids = set()
        user_changes = []

        for partner in self.env['res.partner'].sudo().browse(partner_ids):
            contact_partners = partner.child_ids or [partner]
            for contact in contact_partners:
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'wizard_id': self.id,
                        'in_edx': contact.edx_active,
                    }))
        self.user_ids = user_changes

    @api.multi
    def action_apply(self):
        self.ensure_one()
        self.env['res.partner'].check_access_rights('write')

        for wizard_user in self.user_ids:
            if wizard_user.in_edx:
                if not wizard_user.partner_id.get_user():
                    wizard_user.partner_id.create_edx_user()
                    wizard_user.with_context(
                        active_test=True)._send_email()
                else:
                    wizard_user.partner_id.update_edx_user(True)
                self.refresh()
            elif wizard_user.partner_id.get_user():
                wizard_user.partner_id.update_edx_user(False)
        return {'type': 'ir.actions.act_window_close'}


class EdxWizardUser(models.TransientModel):
    """
        A model to configure users in the edx wizard.
    """

    _name = 'edx.wizard.user'
    _description = 'EDX User Config'

    wizard_id = fields.Many2one(
        'edx.wizard', string='Wizard', required=True, ondelete='cascade')
    partner_id = fields.Many2one(
        'res.partner', string='Contact')
    name = fields.Char(string="Nome", related="partner_id.name")
    email = fields.Char('Email', related="partner_id.email", readonly=True)
    in_edx = fields.Boolean(
        'In EDX')

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

#     @api.multi
#     def get_error_messages(self):
#         emails = []
#         partners_error_empty = self.env['res.partner']
#         partners_error_emails = self.env['res.partner']

#         for wizard_user in self.with_context(active_test=False).filtered(
#                 lambda w: w.in_edx):
#             email = extract_email(wizard_user.email)
#             if not email:
#                 partners_error_empty |= wizard_user.partner_id
#             elif email in emails:
#                 partners_error_emails |= wizard_user.partner_id
#             emails.append(email)

#         error_msg = []
#         if partners_error_empty:
#             error_msg.append(
#                 "%s\n- %s" % (_("Some contacts don't have a valid email: "),
#                               '\n- '.join(partners_error_empty.mapped(
#                                   'display_name'))))
#         if partners_error_emails:
#             error_msg.append(
#                 "%s\n- %s" % (_(
#                     "Several contacts have the same email: "),
#                     '\n- '.join(partners_error_emails.mapped('email'))))
#         if error_msg:
#             error_msg.append(
#                 _("To resolve this error, you can: \n"
#                   "- Correct the emails of the relevant contacts\n"
#                   "- Grant access only to contacts with unique emails"))
#         return error_msg

#     def get_user(self):
#         token = self.get_token()
#         session = requests.Session()
#         username = self.partner_id.edx_username
#         url_api = 'http://52.55.244.3:8080/api/user/v1/accounts/' + username

#         header = {
#             'Content-Type': 'application/merge-patch+json',
#             'Authorization': 'JWT ' + token
#         }

#         url_api = 'http://52.55.244.3:8080//user_api/v1/account/registration/'
#         request = session.patch(url_api, headers=header)

#         if request.status_code == 200:
#             return True
#         else:
#             return False

#     def create_edx_user(self):
#         session = requests.Session()
#         partner_id = self.partner_id
#         username = partner_id.email.split('@')[0] + str(partner_id.id)
#         mailing_address = (partner_id.street, ", ", partner_id.street2, ", ",
#                            partner_id.number, ", ", partner_id.district, ", ",
#                            partner_id.zip)
#         payload = {
#             'email': partner_id.email,
#             'name': partner_id.name,
#             'username': username,
#             'password': partner_id.edx_password,
#             'mailing_address': mailing_address,
#             'city': partner_id.city_id.name,
#             'country': partner_id.country_id.code,
#             'goals': 'Be the best in Odoo',
#             'terms_of_service': 'true',
#             'honor_code': 'true'
#         }

#         url_api = 'http://52.55.244.3:8080//user_api/v1/account/registration/'
#         # url_api = 'http://104.156.230.114//user_api/v1/account/registration/'

#         request = session.post(url_api, data=payload)

#         if request != 200:
#             raise UserError('Não foi possível registrar o usuário')

#         self.partner_id.write({'edx_username': username})
#         self.update_edx_user(True)

#     def get_token(self):
#         session = requests.Session()

#         url_api = 'http://52.55.244.3:8080/oauth2/access_token'

#         payload = {
#             'grant_type': 'client_credentials',
#             'client_id': '7f447db1ceffbf04410e',
#             'client_secret': 'c288965eefe735fe193932d658c464a426c73ce5',
#             'token_type': 'jwt'
#         }

#         request = session.post(url_api, data=payload)

#         if request.status_code == 200:
#             return request.json().get('access_token')

#         raise(request.text)

#     @api.multi
#     def update_edx_user(self, active):
#         token = self.get_token()
#         session = requests.Session()
#         username = self.partner_id.edx_username

#         header = {
#             'Content-Type': 'application/merge-patch+json',
#             'Authorization': 'JWT ' + token
#         }

#         payload = json.dumps({
#             'is_active': active,
#         })

#         url_api = 'http://52.55.244.3:8080/api/user/v1/accounts/' + username
#         request = session.patch(url_api, data=payload, headers=header)

#         if request.status_code != 200:
#             raise UserError('Não foi possível ativar o usuário: ', username)

#         self.enrollment(username, self.get_courses())

#     @api.multi
#     def get_courses(self):
#         session = requests.Session()
#         token = self.get_token()

#         header = {
#             'Authorization': 'JWT ' + token
#         }

#         url_api = 'http://52.55.244.3:8080/api/courses/v1/courses/'

#         request = session.post(url_api, headers=header)

#         if request.status_code == 200:
#             return request.json()

#         raise(request.text)

#     @api.multi
#     def enrollment(self, username, courses, active=True):
#         for course in courses:
#             session = requests.Session()
#             token = self.get_token()

#             header = {
#                 'Authorization': 'JWT ' + token
#             }

#             url_api = 'http://52.55.244.3:8080/api/enrollment/v1/enrollment'

#             payload = {
#                 'user': username,
#                 'is_active': active,
#                 'course_details': {
#                     'course_id': course
#                 }
#             }

#             request = session.post(url_api, headers=header, data=payload)

#             if request.status_code != 200:
#                 raise UserError(
#                     'Não foi possível registrar o usuário:', username,
#                     ' no curso:', course)

#     @api.multi
#     def action_apply(self):
#         import ipdb
#         ipdb.set_trace()
#         self.env['res.partner'].check_access_rights('write')

#         error_msg = self.get_error_messages()
#         if error_msg:
#             raise UserError("\n\n".join(error_msg))

#         for wizard_user in self.sudo().with_context(active_test=False):
#             if wizard_user.in_edx:
#                 if not self.get_user():
#                     password_charset = string.ascii_letters + string.digits
#                     password = gen_random_string(password_charset, 32)
#                     username = (self.partner_id.email.split('@')[0] +
#                                 str(self.partner_id.id))
#                     self.partner_id.write({
#                         'edx_username': username,
#                         'edx_password': password,
#                         'edx_active': True
#                     })
#                     wizard_user.with_context(active_test=True)._send_email()
#                     wizard_user.create_edx_user()
#                 else:
#                     wizard_user.update_edx_user(True)
#                 wizard_user.refresh()
#             else:
#                 self.partner_id.write({
#                     'edx_active': True,
#                 })
#                 wizard_user.update_edx_user(False)

#     @api.multi
#     def _send_email(self):
#         """ send notification email to a new edx user """
#         if not self.env.user.email:
#             raise UserError(_(
#                 'You must have an email address in your' +
#                 ' User Preferences to send emails.'))

#         # determine subject and body in the edx user's language
#         template = self.env.ref(
#             'edx_integration.mail_template_data_edx_welcome')
#         for wizard_line in self:
#             lang = wizard_line.partner_id.lang
#             partner = wizard_line.partner_id

#             edx_url = partner.with_context(
#                 signup_force_type_in_url='',
#                 lang=lang)._get_signup_url_for_action()[partner.id]
#             partner.signup_prepare()

#             if template:
#                 template.with_context(
#                     dbname=self._cr.dbname, edx_url=edx_url,
#                     lang=lang).send_mail(wizard_line.id, force_send=True)
#             else:
#                 _logger.warning(
#                     "No email template found for sending" +
#                     " email to the edx user")

#         return True

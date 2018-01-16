# -*- coding: utf-8 -*-
# © 2018 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import requests
import random
import string

from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''


def gen_random_string(char_set, length):
    if not hasattr(gen_random_string, "rng"):
        gen_random_string.rng = random.SystemRandom()
    return ''.join([gen_random_string.rng.choice(char_set)
                    for _ in range(length)])


class EdxWizard(models.TransientModel):
    """
        A wizard to manage the creation/removal of EDX users.
    """

    _name = 'edx.wizard'
    _description = 'EDX Access Management'

    def _default_edx(self):
        return self.env['res.groups'].search([('name', '=', 'EDX')], limit=1)

    edx_group = fields.Many2one(
        'res.groups', required=True, string='EDX', default=_default_edx)
    user_ids = fields.One2many('edx.wizard.user', 'wizard_id', string='Users')
    welcome_message = fields.Text(
        'Invitation Message',
        help="This text is included in the email sent" +
        " to new users of the edx.")

    @api.onchange('welcome_message')
    def onchange_welcome_message(self):
        edx_group = self._default_edx()
        partner_ids = self.env.context.get('active_ids', [])
        contact_ids = set()
        user_changes = []
        for partner in self.env['res.partner'].sudo().browse(partner_ids):
            contact_partners = partner.child_ids or [partner]
            for contact in contact_partners:
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    in_edx = False
                    if contact.user_ids:
                        in_edx =\
                            edx_group in contact.user_ids[0].groups_id
                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'email': contact.email,
                        'in_edx': in_edx,
                    }))
        self.user_ids = user_changes

    @api.multi
    def action_apply(self):
        self.ensure_one()
        self.user_ids.action_apply()
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
        'res.partner', string='Contact', required=True, readonly=True,
        ondelete='cascade')
    email = fields.Char('Email')
    in_edx = fields.Boolean('In EDX')
    user_id = fields.Many2one('res.users', string='Login User')

    @api.multi
    def get_error_messages(self):
        emails = []
        partners_error_empty = self.env['res.partner']
        partners_error_emails = self.env['res.partner']
        partners_error_user = self.env['res.partner']

        for wizard_user in self.with_context(active_test=False).filtered(
                lambda w: w.in_edx and not w.partner_id.user_ids):
            email = extract_email(wizard_user.email)
            if not email:
                partners_error_empty |= wizard_user.partner_id
            elif email in emails:
                partners_error_emails |= wizard_user.partner_id
            user = self.env['res.users'].sudo().with_context(
                active_test=False).search([('login', '=', email)])
            if user:
                partners_error_user |= wizard_user.partner_id
            emails.append(email)

        error_msg = []
        if partners_error_empty:
            error_msg.append(
                "%s\n- %s" % (_("Some contacts don't have a valid email: "),
                              '\n- '.join(partners_error_empty.mapped(
                                  'display_name'))))
        if partners_error_emails:
            error_msg.append(
                "%s\n- %s" % (_(
                    "Several contacts have the same email: "),
                    '\n- '.join(partners_error_emails.mapped('email'))))
        if partners_error_user:
            error_msg.append(
                "%s\n- %s" % (_(
                    "Some contacts have the same email as" +
                    " an existing edx user:"),
                    '\n- '.join(['%s <%s>' % (
                        p.display_name, p.email)
                        for p in partners_error_user])))
        if error_msg:
            error_msg.append(
                _("To resolve this error, you can: \n"
                  "- Correct the emails of the relevant contacts\n"
                  "- Grant access only to contacts with unique emails"))
        return error_msg

    def create_edx_user(self):
        s = requests.Session()

        username = self.user_id.login.split('@')[0] + str(self.user_id.id)
        payload = {
            'email': self.user_id.login,
            'name': self.user_id.name,
            'username': username,
            'password': self.user_id.edx_password,
            'level_of_education': 'none',
            'gender': '',
            'year_of_birth': '1998',
            'mailing_address': '',
            'goals': 'Be the best in Odoo',
            'terms_of_service': 'true',
            'honor_code': 'true'
        }

        url_api = 'http://52.55.244.3:8080//user_api/v1/account/registration/'

        r = s.post(url_api, data=payload)
        print(r.text)
        self.update_edx_user(username)

    def update_edx_user(self, username):
        s = requests.Session()

        payload = {
            'active': True,
        }

        url_api = 'http://52.55.244.3:8080/api/user/v1/accounts/' + username
        r = s.post(url_api, data=payload)
        print(r.text)

    @api.multi
    def action_apply(self):
        self.env['res.partner'].check_access_rights('write')

        error_msg = self.get_error_messages()
        if error_msg:
            raise UserError("\n\n".join(error_msg))

        for wizard_user in self.sudo().with_context(active_test=False):
            edx_group = wizard_user.wizard_id.edx_group
            user = wizard_user.partner_id.user_ids[0] if \
                wizard_user.partner_id.user_ids else None
            # update partner email, if a new one was introduced
            if wizard_user.partner_id.email != wizard_user.email:
                wizard_user.partner_id.write({'email': wizard_user.email})
            # add edx group to relative user of selected partners
            if wizard_user.in_edx:
                user_edx = None
                if not user:
                    if wizard_user.partner_id.company_id:
                        company_id = wizard_user.partner_id.company_id.id
                    else:
                        company_id = self.env[
                            'res.company']._company_default_get(
                            'res.users')
                    user_edx = wizard_user.sudo().with_context(
                        company_id=company_id)._create_user()
                else:
                    user_edx = user
                wizard_user.write({'user_id': user_edx.id})
                if not wizard_user.user_id.active or \
                        edx_group not in wizard_user.user_id.groups_id:
                    wizard_user.user_id.write({
                        'active': True,
                        'groups_id': [(4, edx_group.id)]})
                    # prepare for the signup process
                    wizard_user.user_id.partner_id.signup_prepare()
                    password_charset = string.ascii_letters + string.digits
                    user_edx_password = gen_random_string(password_charset, 32)
                    wizard_user.user_id.write({
                        'edx_password': user_edx_password})
                    wizard_user.with_context(active_test=True)._send_email()

                wizard_user.refresh()
                wizard_user.create_edx_user()
            else:
                # remove the user (if it exists) from the edx group
                if user and edx_group in user.groups_id:
                    # if user belongs to edx only, deactivate it
                    if len(user.groups_id) <= 1:
                        user.write(
                            {'groups_id': [(3, edx_group.id)],
                             'active': False})
                    else:
                        user.write({'groups_id': [(3, edx_group.id)]})

    @api.multi
    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        company_id = self.env.context.get('company_id')
        return self.env['res.users'].with_context(
            no_reset_password=True).create({
                'email': extract_email(self.email),
                'login': extract_email(self.email),
                'partner_id': self.partner_id.id,
                'company_id': company_id,
                'company_ids': [(6, 0, [company_id])],
                'groups_id': [(6, 0, [])],
            })

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
            lang = wizard_line.user_id.lang
            partner = wizard_line.user_id.partner_id

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

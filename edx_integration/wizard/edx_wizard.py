# -*- coding: utf-8 -*-
# © 2018 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools import email_split

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

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
            else:
                wizard_user.partner_id.write({'edx_active': False})
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

# © 2018 Danimar Ribeiro <danimaibeiro@gmail.com> Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
except ImportError:
    _logger.warning('Cannot import twilio')


class SmsApi(models.AbstractModel):
    _inherit = 'sms.api'

    @api.model
    def _send_sms(self, numbers, message):
        sid = self.env.user.company_id.twilio_account_sid
        token = self.env.user.company_id.twilio_auth_token
        from_number = self.env.user.company_id.twilio_number
        client = Client(sid, token)
        for number in numbers:
            client.api.account.messages.create(
                to=number,
                from_=from_number,
                body=message)

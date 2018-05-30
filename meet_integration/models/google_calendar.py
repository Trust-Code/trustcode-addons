# © 2018 Danimar Ribeiro <danimaribeiro@gmail.com> Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import uuid
import json
import requests
import logging
from datetime import datetime
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    use_meet = fields.Boolean('Usar Meet?', default=True)
    meet_request_id = fields.Char('Meet Request Id')
    meet_link = fields.Char('Meeting Link')

    @api.model
    def sincronize_google_meet(self):
        meetings = self.search(
            [('use_meet', '=', True), ('meet_link', '=', None),
             ('start_datetime', '>=', datetime.now())])
        for meet in meetings:
            meet.meet_request_id = str(uuid.uuid1())
            meet.create_an_event_for_meet()

    def create_an_event_for_meet(self):
        data = {
            "end": {
                "date": self.end_date or self.end_datetime
            },
            "start": {
                "date": self.start_date or self.start_datetime
            },
            "description": self.description,
            "summary": self.name,
            "conferenceData": {
                "createRequest": {
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    },
                    "requestId": self.meet_request_id
                }
            }
        }
        url = "https://www.googleapis.com/calendar/v3/calendars/gestao@trustcode.com.br/events"

        scope = 'https://www.googleapis.com/auth/calendar'

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data_json = json.dumps(data)

        res = requests.request('POST', url, data=data_json, headers=headers)
        res.raise_for_status()
        status = res.status_code

        if int(status) in (204, 404):  # Page not found, no response
            response = False
        else:
            response = res.json()
            print(response)

    def delete_meet_event(self):
        pass

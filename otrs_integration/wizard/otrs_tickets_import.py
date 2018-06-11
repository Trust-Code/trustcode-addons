# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.exceptions import UserError


class OtrsTicketsImport(models.TransientModel):
    _name = 'otrs.tickets.import'

    def import_otrs_tickets(self):
        response = self.env.user.otrs_search('Ticket')
        if "TicketID" in response.text:
            self.env['helpdesk.ticket'].import_tickets_from_otrs(
                response.json()["TicketID"])
        else:
            raise UserError("Erro ao importar tickets: {}".format(
                response.content))

# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    otrs_id = fields.Char('ID OTRS')
    otrs_link = fields.Char('Link OTRS')

    _sql_constraints = [('otrs_id_uniq', 'unique(otrs_id)',
                         'The OTRS ID must be unique')]

    def import_tickets_from_otrs(self, ids):
        return True

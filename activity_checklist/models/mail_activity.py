# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    activity_checklist_id = fields.Many2one(
        'mail.activity.checklist', 'Checklist')

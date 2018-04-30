# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MailActivityChecklist(models.Model):
    _name = 'mail.activity.checklist'

    name = fields.Char('Nome')
    activitiy_ids = fields.One2many(
        'mail.activity', 'activity_checklist_id', 'Atividades')

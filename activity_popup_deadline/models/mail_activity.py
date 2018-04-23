# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTFT


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    datetime_deadline = fields.Datetime('Data de Vencimento')
    notification_time = fields.Integer('Lembrete')
    notification_interval = fields.Selection(
        [('minutes', 'Minutos'),
         ('hours', 'Horas'),
         ('days', 'Dias')], 'Intervalo', default="minutes")

    def update_date_deadline(self, vals):
        datetime_value = datetime.strptime(vals['datetime_deadline'], DTFT)
        vals.update({'date_deadline': datetime.strftime(
            datetime_value.date(), DTFT)})
        return vals

    @api.model
    def create(self, vals):
        self.env.user.notify_info('MANO DO CEU')
        if vals.get('datetime_deadline'):
            vals = self.update_date_deadline(vals)
        return super(MailActivity, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('datetime_deadline'):
            vals = self.update_date_deadline(vals)
        return super(MailActivity, self).write(vals)

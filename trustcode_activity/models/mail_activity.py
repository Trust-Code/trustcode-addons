# © 2018 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    date_deadline = fields.Datetime()

    alarm_ids = fields.Many2many('calendar.alarm', string='Reminders',
                                 ondelete="restrict", copy=False)


class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    activity_date_deadline = fields.Datetime()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    activity_date_deadline = fields.Datetime()

# -*- coding: utf-8 -*-
# © 2015 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil.parser import parse

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    days_in_current_stage = fields.Integer(string="Dias no estágio atual",
                                           compute="_days_in_current_stage",
                                           store=True)
    days_since_creation = fields.Integer(string="Dias desde a criação",
                                         compute="_days_since_creation",
                                         store=True)
    is_late = fields.Boolean(string="Atrasada?", compute="_is_late",
                             store=True)
    interactions = fields.One2many('crm.activity.log', 'lead_id',
                                   string="Interações")

    @api.depends('date_last_stage_update')
    def _days_in_current_stage(self):
        for record in self:
            record.days_in_current_stage = (
                datetime.now() - parse(record.date_last_stage_update)).days

    @api.depends('create_date')
    def _days_since_creation(self):
        for record in self:
            record.days_since_creation = (
                datetime.today() - parse(record.create_date)).days

    @api.depends('stage_id')
    def _is_late(self):
        for record in self:
            record.is_late = record.stage_id.maximum_days < \
                             record.days_in_current_stage

# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    commitment_date = fields.Datetime(
        'Data do Compromisso', track_visibility='onchange')
    requisition_date = fields.Datetime(
        'Data do Requisição', track_visibility='onchange')

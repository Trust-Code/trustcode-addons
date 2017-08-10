# -*- coding: utf-8 -*-
# © 2015 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    maximum_days = fields.Integer(string=u"Máximo de dias neste estágio")

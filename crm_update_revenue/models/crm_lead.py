# -*- coding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    recurrent_revenue = fields.Float(string='Receita Recorrente',
                                     oldname="x_receita_recorrente")

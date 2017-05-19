# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class PaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    invoice_day=fields.Integer(
        string="Incoive Day",
        help='Set the date for invoice create')
    indPag=fields.Selection(selection_add=[('3', 'Mensalidade')])

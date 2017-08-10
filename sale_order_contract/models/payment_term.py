# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class PaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    invoice_day = fields.Integer(
        string=u"Data da Fatura",
        help=u'Define o dia que será criado a fatura')
    indPag = fields.Selection(selection_add=[('3', u'Mensalidade')])

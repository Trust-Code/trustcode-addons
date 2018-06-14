# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from lxml.html import document_fromstring


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    quotation_description = fields.Html(string="Descrição (html)")

    @api.onchange('quotation_description')
    def onchange_description(self):
        self.name = self.clean_html_text(self.quotation_description)

    def clean_html_text(self, string):
        doc = document_fromstring(string.replace('</p>', '\r\n'))
        return doc.text_content()

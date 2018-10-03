
# -*- coding: utf-8 -*-
#© 2018 Trustcode / Adaptado por Augusto D. Lisbôa
#License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from lxml.html import document_fromstring

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    quotation_description = fields.Html(string="Descrição")

    @api.onchange('quotation_description')
    def onchange_description(self):
        if self.quotation_description:
            self.name = self.clean_html_text(self.quotation_description)

    def clean_html_text(self, string):
        doc = document_fromstring(string.replace('</p>', '\r\n'))
        return doc.text_content()

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.quotation_description = self.product_id.display_name
		if self.product_id.variant_description_sale:
            self.quotation_description = self.product_id.variant_description_sale
		
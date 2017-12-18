# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class DiscountSaleReport(models.Model):
    _inherit = 'sale.report'

    discount = fields.Float('Discount', readonly=True)

    def _select(self):
        res = super(DiscountSaleReport, self)._select()
        select_str = res+""",sum(l.product_uom_qty / u.factor * u2.factor *
            cr.rate * l.price_unit * l.discount / 100.0) as discount"""
        return select_str

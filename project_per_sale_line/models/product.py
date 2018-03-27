# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class Product(models.Model):
    _inherit = 'product.product'

    project_name = fields.Char('Nome do projeto')

    @api.model
    def create(self, vals):
        res = super(Product, self).create(vals)
        res.project_name = res.product_tmpl_id.name
        return res

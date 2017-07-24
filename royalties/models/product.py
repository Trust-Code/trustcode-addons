# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    contract_ids = fields.One2many(
        'royalties.lines',
        'royalties_id')

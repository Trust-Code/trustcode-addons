# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    discount_rules_ids = fields.One2many('discount.rules', 'sale_config_id',
                                         string="Regras de Desconto")

# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class SaleConfiguration(models.TransientModel):
    _name = 'sale.config.settings'
    _inherit = 'sale.config.settings'

    discount_rules_ids = fields.One2many('discount.rules', 'sale_config_id',
                                         string="Regras de Desconto",
                                         default_model="discount.rules")

    @api.model
    def get_default_discount_rule_ids(self, fields):
        params = self.env['ir.config_parameter']
        discount_rules_ids = params.get_param('discount_rules_ids')
        return {'discount_rules_ids': safe_eval(discount_rules_ids)}

    @api.multi
    def set_default_discount_rule_ids(self):
        self.env['ir.config_parameter'].set_param('discount_rules_ids',
                                                  self.discount_rules_ids.ids)

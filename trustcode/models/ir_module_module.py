# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo
from odoo import api, models
from odoo.exceptions import UserError


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.multi
    def button_install(self):
        test_enabled = odoo.tools.config['test_enable']
        if not test_enabled:
            raise UserError(
                'Contate o suporte Trustcode para instalar módulos\n'
                'meajuda@trustcode.com.br')
        return super(IrModuleModule, self).button_install()

    @api.multi
    def button_immediate_install(self):
        test_enabled = odoo.tools.config['test_enable']
        if not test_enabled:
            raise UserError(
                'Contate o suporte Trustcode para instalar módulos\n'
                'meajuda@trustcode.com.br')
        return super(IrModuleModule, self).button_immediate_install()

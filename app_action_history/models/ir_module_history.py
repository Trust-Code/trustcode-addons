# -*- coding: utf-8 -*-
from odoo import models, fields, api


class IrModuleHistory(models.Model):
    _name = 'ir.module.history'

    TYPES = [
        ('install', 'Installed'),
        ('upgrade', 'Upgraded'),
        ('uninstall', 'Uninstalled'),
    ]

    module_name = fields.Char(required=True, string='Module')
    type = fields.Selection(TYPES, required=True, string='Action')
    user_id = fields.Many2one('res.users', string='Author', required=True)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def _button_immediate_function(self, function):
        res = super(IrModuleModule, self)._button_immediate_function(function)
        for module in self:
            action_type = {
                'button_install': 'install',
                'button_upgrade': 'upgrade',
                'button_uninstall': 'uninstall',
            }.get(function.__name__)

            if action_type:
                self.env['ir.module.history'].sudo().create({
                    'module_name': module.name,
                    'type': action_type,
                    'user_id': self._uid,
                })
        return res

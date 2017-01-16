# -*- coding: utf-8 -*-
# © 2016 Alessandro Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    version = fields.Integer(u'Versão', compute='_compute_version')

    @api.multi
    def _compute_version(self):
        obj_attach = self.env['ir.attachment'].search(
            [('res_id', '=', self.id)],
            order='id desc', limit=1)

        self.version = obj_attach.res_version


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    res_version = fields.Integer(u'Versão', size=4)

    @api.model
    def create(self, values):
        if 'res_model' in values and values['res_model'] == 'sale.order':
            obj_so = self.env['sale.order'].browse(values['res_id'])
            get_version = obj_so.version

            if get_version:
                values.update({'res_version': get_version + 1})
            else:
                values.update({'res_version': 1})
        return super(IrAttachment, self).create(values)

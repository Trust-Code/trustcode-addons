# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class Services(models.Model):
    _name = 'mail.services'

    @api.multi
    def name_get(self):
        return [(rec.id, rec.description) for rec in self]

    identificador = fields.Integer(string='Identificação')
    description = fields.Char(string="Descrição")
    service_cod = fields.Integer(string='Código')
    stock_pick_id = fields.One2many(comodel_name='stock.picking',
                                    inverse_name='service_id',
                                    string='')

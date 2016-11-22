# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_type = fields.Selection(related="carrier_id.delivery_type",
                                     string="Tipo integração")
    service_id = fields.Many2one('delivery.correios.service', string="Serviço",
                                 domain="[('delivery_id', '=', carrier_id)]")

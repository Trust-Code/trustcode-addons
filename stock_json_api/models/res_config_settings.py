# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pick_type_incoming_id = fields.Many2one(
        'stock.picking.type', string="Tipo de Recebimento")
    pick_type_stock_id = fields.Many2one(
        'stock.picking.type', string="Tipo de Armazenamento")
    pick_type_order_id = fields.Many2one(
        'stock.picking.type', string="Tipo de Pedido Recebido")
    pick_type_pack_id = fields.Many2one(
        'stock.picking.type', string="Tipo de Packing")
    pick_type_outgoing_id = fields.Many2one(
        'stock.picking.type', string="Tipo de Entrega")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            pick_type_incoming_id=int(params.get_param(
                'json_api.pick_type_incoming_id', default=False)) or False,
            pick_type_stock_id=int(params.get_param(
                'json_api.pick_type_stock_id', default=False)) or False,
            pick_type_order_id=int(params.get_param(
                'json_api.pick_type_order_id', default=False)) or False,
            pick_type_pack_id=int(params.get_param(
                'json_api.pick_type_pack_id', default=False)) or False,
            pick_type_outgoing_id=int(params.get_param(
                'json_api.pick_type_outgoing_id', default=False)) or False,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "json_api.pick_type_incoming_id", self.pick_type_incoming_id.id)

        self.env['ir.config_parameter'].sudo().set_param(
            "json_api.pick_type_stock_id", self.pick_type_stock_id.id)

        self.env['ir.config_parameter'].sudo().set_param(
            "json_api.pick_type_order_id", self.pick_type_order_id.id)

        self.env['ir.config_parameter'].sudo().set_param(
            "json_api.pick_type_pack_id", self.pick_type_pack_id.id)

        self.env['ir.config_parameter'].sudo().set_param(
            "json_api.pick_type_outgoing_id", self.pick_type_outgoing_id.id)

# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import requests
import json
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def send_json(self, pick_ids, backorder=False):
        param = self.env["ir.config_parameter"]
        url = param.sudo().get_param('stock.endpoint_stock_delivery')
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.env.user.api_key}
        date = datetime.now()
        date = date.isoformat()

        for item in pick_ids:
            agrupador = item.picking_type_id.agrupador
            if agrupador != "saida":
                continue

            vals = dict(
                order_id=item.origin,
                date=date,
                shippingCompany=dict(
                    driver=item.motorista,
                    board=item.placa,
                ),
                picking_type=item.picking_type_id.name,
                state=item.state,
                backorder=backorder)

            products = []
            for product in item.move_lines:
                item_vals = dict(
                    id=product.product_id.default_code,
                    quantity=product.quantity_done,
                    volume=item.number_of_packages,
                )

                products.append(item_vals)

            vals.update({'products': products})

            post = json.dumps(vals)
            requests.post(url=url, data=post, headers=headers)

    @api.multi
    def action_cancel(self):
        res = super(StockPicking, self).action_cancel()
        self.send_json(self)
        return res


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    agrupador = fields.Selection(
        string="Agrupa picking types",
        selection=[
            ('entrada', 'Entrada'),
            ('saida', 'Saída'),
            ('outros', 'Outros'),
        ],
    )


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        self.env['stock.picking'].send_json(self.pick_ids)
        return res


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        res = super(StockBackorderConfirmation, self).process()
        self.env['stock.picking'].send_json(self.pick_ids, backorder=True)
        return res

    def process_cancel_backorder(self):
        res = super(
            StockBackorderConfirmation, self).process_cancel_backorder()
        self.env['stock.picking'].send_json(self.pick_ids)
        return res

# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
import requests
import json
from datetime import datetime


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        param = self.env["ir.config_parameter"]
        url = param.sudo().get_param('stock.endpoint_stock_delivery')
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.env.user.api_key}
        date = datetime.now()
        date = date.isoformat()

        for item in self.pick_ids:
            dest_id = item.picking_type_id.default_location_dest_id
            if dest_id.usage != "customer":
                continue

            vals = dict(
                order_id=item.origin,
                date=date,
                shippingCompany=dict(
                    driver=item.motorista,
                    board=item.placa,
                ),)

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

        return res

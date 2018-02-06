# -*- encoding: utf-8 -*-
# © 2017 Fábio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
import requests
import json
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        param = self.env["ir.config_parameter"]
        url = param.sudo().get_param('stock.endpoint_stock_delivery')
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.env.user.api_key}
        date = datetime.now()
        date = date.isoformat()

        for item in self:
            dest_id = self.picking_type_id.default_location_dest_id
            if dest_id.usage != "customer":
                continue

            vals = dict(
                order_id=self.origin,
                date=date,
                shippingCompany=dict(
                    driver=self.motorista,
                    board=self.placa,
                ),)

            products = []
            for product in self.move_lines:
                item_vals = dict(
                    id=product.product_id.default_code,
                    quantity=product.quantity_done,
                    volume=self.number_of_packages,
                )

                products.append(item_vals)

            vals.update({'products': products})

            post = json.dumps(vals)
            requests.post(url=url, data=post, headers=headers)

        return res

# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied


def cnpj_cpf_format(cnpj_cpf):
    if len(cnpj_cpf) == 14:
        cnpj_cpf = (cnpj_cpf[0:2] + '.' + cnpj_cpf[2:5] +
                    '.' + cnpj_cpf[5:8] +
                    '/' + cnpj_cpf[8:12] +
                    '-' + cnpj_cpf[12:14])
    else:
        cnpj_cpf = (cnpj_cpf[0:3] + '.' + cnpj_cpf[3:6] +
                    '.' + cnpj_cpf[6:9] + '-' + cnpj_cpf[9:11])
    return cnpj_cpf


class ApiStock(http.Controller):

    def _validate_key(self, json):
        key = json['api_key']
        user = request.env['res.users'].sudo().search([('api_key', '=', key)])
        if not user:
            raise AccessDenied()

        return user

    @http.route('/api/stock/incoming', type='json', auth="public",
                methods=['POST'], csrf=False)
    def api_stock_incoming(self, **kwargs):
        user = self._validate_key(request.jsonrequest)
        picking_id = self._save_incoming_order(request.jsonrequest, user)

        return json.dumps({"picking_id": picking_id})

    @http.route('/api/stock/outgoing', type='json', auth="public",
                methods=['POST'], csrf=False)
    def api_stock_outgoing(self, **kwargs):
        user = self._validate_key(request.jsonrequest)
        picking_id = self._save_outgoing_order(request.jsonrequest, user)

        return json.dumps({"picking_id": picking_id})

    @http.route('/api/stock/cancel_outgoing', type='json', auth="public",
                methods=['POST'], csrf=False)
    def api_stock_cnacel_outgoing(self, **kwargs):
        user = self._validate_key(request.jsonrequest)
        picking_id = self._cancel_outgoing_order(request.jsonrequest, user)

        return json.dumps({"picking_id": picking_id})

    def _save_incoming_order(self, compra, user):
        env_partner = request.env['res.partner'].sudo(user)
        cnpj = cnpj_cpf_format(compra['provider']['cnpj'])
        partner = env_partner.search([('cnpj_cpf', '=', cnpj)])

        vals = {
            'name': compra['provider']['name'],
            'cnpj_cpf': cnpj,
            'phone': compra['provider']['phone'],
            'email': compra['provider']['email'],
        }
        if not partner:
            partner = env_partner.create(vals)

        env_picking_type = request.env['stock.picking.type'].sudo(user)
        env_stock = request.env['stock.warehouse'].sudo(user)
        env_product = request.env['product.product'].sudo(user)
        env_uom = request.env['product.uom'].sudo(user)

        picking_items = []
        for item in compra['products']:
            product = env_product.search([('default_code', '=', item['id'])])
            uom = env_uom.with_context(
                {'lang': 'en_US'}).search(
                    [('name', '=ilike', item['weight_class'])])
            vals = {
                'name': item['name'],
                'list_price': item['valor'],
                'uom_id': uom.id,
                'uom_po_id': uom.id,
                'type': 'product',
                'default_code': item['id'],
            }
            if not product:
                product = env_product.create(vals)

            picking_items.append((0, 0, {
                'name': product[0].name,
                'product_id': product[0].id,
                'product_uom_qty': item['quantity'],
                'ordered_qty': item['quantity'],
                'product_uom': uom.id,
            }))

        pick_type = env_picking_type.search(
            [('code', '=', 'incoming')], limit=1)

        if pick_type.default_location_src_id:
            location_id = pick_type.default_location_src_id.id
        elif partner:
            location_id = partner[0].property_stock_supplier.id
        else:
            dummy, location_id = env_stock._get_partner_locations()

        if pick_type.default_location_dest_id:
            location_dest_id = pick_type.default_location_dest_id.id
        elif partner:
            location_dest_id = partner.property_stock_customer.id
        else:
            location_dest_id, dummy = env_stock._get_partner_locations()

        picking = request.env['stock.picking'].sudo(user).create({
            'name': pick_type.sequence_id.next_by_id(),
            'partner_id': partner[0].id,
            'picking_type_id': pick_type.id,
            'move_lines': picking_items,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
        })
        return picking.id

    def _save_outgoing_order(self, venda, user):
        venda = venda['body']['orders'][0]
        env_partner = request.env['res.partner'].sudo(user)
        cnpj = cnpj_cpf_format(venda['cpf'])
        partner = env_partner.search([('cnpj_cpf', '=', cnpj)])

        vals = {
            'name': "%s %s" % (venda['shipping_firstname'],
                               venda['shipping_lastname']),
            'cnpj_cpf': cnpj,
            'phone': venda['telephone'],
            'mobile': venda['cellphone'],
            'email': venda['email'],
            'street': venda['shipping_address_1'],
            'street2': venda['shipping_address_2'],
            'zip': venda['shipping_postcode'],

        }
        if not partner:
            partner = env_partner.create(vals)

        env_picking_type = request.env['stock.picking.type'].sudo(user)
        env_stock = request.env['stock.warehouse'].sudo(user)
        env_product = request.env['product.product'].sudo(user)
        env_uom = request.env['product.uom'].sudo(user)

        picking_items = []
        for item in venda['products']:
            product = env_product.search(
                [('default_code', '=', item['product_id'])])
            uom = env_uom.with_context(
                {'lang': 'en_US'}).search(
                    [('name', '=ilike', item['weight_class'])])
            vals = {
                'name': item['name'],
                'list_price': item['price'],
                'uom_id': uom.id,
                'uom_po_id': uom.id,
                'type': 'product',
                'default_code': item['product_id'],
            }
            if not product:
                product = env_product.create(vals)

            picking_items.append((0, 0, {
                'name': product[0].name,
                'product_id': product[0].id,
                'product_uom_qty': item['quantity'],
                'ordered_qty': item['quantity'],
                'product_uom': uom.id,
            }))

        pick_type = env_picking_type.search(
            [('code', '=', 'outgoing')], limit=1)

        if pick_type.default_location_src_id:
            location_id = pick_type.default_location_src_id.id
        elif partner:
            location_id = partner[0].property_stock_supplier.id
        else:
            dummy, location_id = env_stock._get_partner_locations()
        if pick_type.default_location_dest_id:
            location_dest_id = pick_type.default_location_dest_id.id
        elif partner:
            location_dest_id = partner.property_stock_customer.id
        else:
            location_dest_id, dummy = env_stock._get_partner_locations()

        ids = []

        picking_ref = request.env.ref('picking.a').sudo(user)

        picking = request.env['stock.picking'].sudo(user).create({
            'name': pick_type.sequence_id.next_by_id(),
            'partner_id': partner[0].id,
            'picking_type_id': picking_ref.id,
            'move_lines': picking_items,
            'location_id': picking_ref.default_location_src_id.id,
            'location_dest_id': picking_ref.default_location_dest_id.id,
            'origin': venda['order_id'],
        })
        ids.append(picking.id)

        packing_ref = request.env.ref('packing.b').sudo(user)

        packing = request.env['stock.picking'].sudo(user).create({
            'name': pick_type.sequence_id.next_by_id(),
            'partner_id': partner[0].id,
            'picking_type_id': packing_ref.id,
            'move_lines': picking_items,
            'location_id': packing_ref.default_location_src_id.id,
            'location_dest_id': packing_ref.default_location_dest_id.id,
            'origin': venda['order_id'],
        })
        ids.append(packing.id)

        requested_order_ref = request.env.ref('received_order.c').sudo(user)

        requested_order = request.env['stock.picking'].sudo(user).create({
            'name': pick_type.sequence_id.next_by_id(),
            'partner_id': partner[0].id,
            'picking_type_id': requested_order_ref.id,
            'move_lines': picking_items,
            'location_id': requested_order_ref.default_location_src_id.id,
            'location_dest_id': (requested_order_ref
                                 .default_location_dest_id.id),
            'origin': venda['order_id'],
        })
        ids.append(requested_order.id)

        if len(ids) > 0:
            return ids
        else:
            raise Exception("Os ids externos para os pickings referenciados não foram\
 encontrados.")

    def _cancel_outgoing_order(self, venda, user):
        venda = venda['body']['orders'][0]
        cancel_requested_order = request.env['stock.picking'].sudo(user)\
            .search([('origin', '=', venda['order_id']), (
                'state', '!=', 'cancel')])
        if any(stock_picking['state'] == 'done' for stock_picking
               in cancel_requested_order):
            raise Exception("Não é possível cancelar pickings que já estão\
 concluídos.")
        cancelled_orders = []
        for stock_picking in cancel_requested_order:
            stock_picking.sudo(user).action_cancel()
            cancelled_orders.append(stock_picking['id'])
        if len(cancelled_orders) > 0:
            return cancelled_orders
        else:
            raise Exception("Não existem pickings relacionados\
 à este order_id para serem cancelados.")

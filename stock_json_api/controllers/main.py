# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import re
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError
from datetime import datetime, timedelta


def cnpj_cpf_format(cnpj_cpf):
    cnpj_cpf = re.sub('[^0-9]', '', cnpj_cpf)
    if len(cnpj_cpf) == 14:
        cnpj_cpf = (cnpj_cpf[0:2] + '.' + cnpj_cpf[2:5] +
                    '.' + cnpj_cpf[5:8] +
                    '/' + cnpj_cpf[8:12] +
                    '-' + cnpj_cpf[12:14])
    elif len(cnpj_cpf) == 11:
        cnpj_cpf = (cnpj_cpf[0:3] + '.' + cnpj_cpf[3:6] +
                    '.' + cnpj_cpf[6:9] + '-' + cnpj_cpf[9:11])
    else:
        raise Exception('CNPJ ou CPF inválido!')

    return cnpj_cpf


class ApiStock(http.Controller):

    def _validate_key(self, json):
        key = json['api_key']
        user = request.env['res.users'].sudo().search(
            [('api_key', '=', key)], limit=1)
        if not user:
            raise AccessDenied()

        return user

    def check_repeated_json(self, json, user):
        try:
            order_id = json['body']['orders'][0]['order_id']
            order_id = str(order_id)
        except KeyError:
            order_id = json['purchaseOrder']
        total = request.env['stock.picking'].sudo(user).search_count([
            ('origin', '=', order_id)
        ])
        if total > 0:
            raise UserError('Este JSON já foi importado.')

    @http.route('/api/stock/incoming', type='json', auth="public",
                methods=['POST'], csrf=False)
    def api_stock_incoming(self, **kwargs):
        user = self._validate_key(request.jsonrequest)
        self.check_repeated_json(request.jsonrequest, user)
        picking_id = self._save_incoming_order(request.jsonrequest, user)

        return json.dumps({"picking_id": picking_id})

    @http.route('/api/stock/outgoing', type='json', auth="public",
                methods=['POST'], csrf=False)
    def api_stock_outgoing(self, **kwargs):
        user = self._validate_key(request.jsonrequest)
        self.check_repeated_json(request.jsonrequest, user)
        picking_id = self._save_outgoing_order(request.jsonrequest, user)

        return json.dumps({"picking_id": picking_id})

    @http.route('/api/stock/cancel_outgoing', type='json', auth="public",
                methods=['POST'], csrf=False)
    def api_stock_cnacel_outgoing(self, **kwargs):
        user = self._validate_key(request.jsonrequest)
        picking_id = self._cancel_outgoing_order(request.jsonrequest, user)

        return json.dumps({"picking_id": picking_id})

    def _get_locations(self, user, partner, pick_type):
        env_stock = request.env['stock.warehouse'].sudo(user)
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
        return location_id, location_dest_id

    def _save_incoming_order(self, compra, user):
        env_partner = request.env['res.partner'].sudo(user)
        cnpj = cnpj_cpf_format(compra['provider']['cnpj'])
        partner = env_partner.search([('cnpj_cpf', '=', cnpj)])

        vals = {
            'name': compra['provider']['name'],
            'legal_name': compra['provider']['name'],
            'cnpj_cpf': cnpj,
            'phone': compra['provider']['phone'],
            'email': compra['provider']['email'],
            'supplier': True,
            'customer': False,
        }
        if not partner:
            partner = env_partner.create(vals)

        if 'contact' in compra['provider'].keys():
            contact_ids = env_partner.search([('parent_id', '=', partner.id)])
            contact = contact_ids.filtered(
                lambda x: x.name == compra['provider']['contact'])

            if not contact:
                vals = {
                    'name': compra['provider']['contact'],
                    'supplier': True,
                    'customer': False,
                    'parent_id': partner.id,
                }

                env_partner.create(vals)

        env_product = request.env['product.product'].sudo(user)
        env_uom = request.env['product.uom'].sudo(user)

        ids = []
        picking_items = []
        for item in compra['products']:
            product = env_product.search([('default_code', '=', item['id'])])

            if not product:
                uom = env_uom.with_context(
                    {'lang': 'en_US'}).search(
                    [('name', '=ilike', item['weight_class'])], limit=1)
                vals = {
                    'name': item['name'],
                    'list_price': item['valor'],
                    'uom_id': uom.id,
                    'uom_po_id': uom.id,
                    'type': 'product',
                    'default_code': item['id'],
                }
                product = env_product.create(vals)

            picking_items.append((0, 0, {
                'name': product[0].name,
                'product_id': product[0].id,
                'product_uom_qty': item['quantity'],
                'ordered_qty': item['quantity'],
                'product_uom': product[0].uom_id.id,
            }))

        schedule = datetime.strptime(
            compra['date'], '%Y-%m-%d')
        schedule += timedelta(hours=23)

        params = request.env['ir.config_parameter'].sudo()
        pick_type_env = request.env['stock.picking.type'].sudo(user)

        pick_incoming_type_id = int(params.get_param(
            'json_api.pick_type_incoming_id', default=False))
        picking_incoming_ref = pick_type_env.browse(pick_incoming_type_id)
        if not picking_incoming_ref:
            raise Exception("Configure os tipos de separação.")

        src_id, dest_id = self._get_locations(
            user, partner, picking_incoming_ref)

        picking = request.env['stock.picking'].sudo(
            user).with_context(planned_picking=True).create({
                'name': picking_incoming_ref.sequence_id.next_by_id(),
                'scheduled_date': schedule,
                'origin': compra['purchaseOrder'],
                'partner_id': partner[0].id,
                'picking_type_id': picking_incoming_ref.id,
                'move_lines': picking_items,
                'location_id': src_id,
                'location_dest_id': dest_id,
            })
        ids.append(picking.id)

        pick_stock_type_id = int(params.get_param(
            'json_api.pick_type_stock_id', default=False))
        picking_stock_ref = pick_type_env.browse(pick_stock_type_id)
        if not picking_stock_ref:
            raise Exception("Configure os tipos de separação.")

        src_id, dest_id = self._get_locations(
            user, partner, picking_stock_ref)

        picking = request.env['stock.picking'].sudo(
            user).with_context(planned_picking=True).create({
                'name': picking_stock_ref.sequence_id.next_by_id(),
                'scheduled_date': schedule,
                'origin': compra['purchaseOrder'],
                'partner_id': partner[0].id,
                'picking_type_id': picking_stock_ref.id,
                'move_lines': picking_items,
                'location_id': src_id,
                'location_dest_id': dest_id,
            })
        ids.append(picking.id)

        return ids

    def _calc_amount_total(self, picking_items):
        total = 0
        for line in picking_items:
            total += line[2]['valor_bruto']
        return total

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
        }
        if not partner:
            partner = env_partner.create(vals)
            payment_adress = {
                'type': 'invoice',
                'zip': venda['payment_postcode'],
                'street': venda['payment_address_1'],
                'district': venda['payment_address_2'],
                'number': venda['payment_custom_field']['1'],
                'street2': venda['payment_custom_field']['2'],
            }
            partner.write({
                'child_ids': [(0, 0, payment_adress)],
            })

        partner.zip_search(
            re.sub('[^0-9]', '', venda['shipping_postcode']))

        shipping_number = ''
        shipping_street2 = ''

        if '1' in venda['shipping_custom_field'].keys():
            shipping_number = venda['shipping_custom_field']['1']

        if '2' in venda['shipping_custom_field'].keys():
            shipping_street2 = venda['shipping_custom_field']['2']

        partner.write({
            'street': venda['shipping_address_1'],
            'district': venda['shipping_address_2'],
            'number': shipping_number,
            'street2': shipping_street2,
        })

        env_product = request.env['product.product'].sudo(user)
        env_uom = request.env['product.uom'].sudo(user)

        picking_items = []
        for item in venda['products']:
            product = env_product.search(
                [('default_code', '=', item['product_id'])])

            if not product:
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
                product = env_product.create(vals)

            picking_items.append((0, 0, {
                'name': product[0].name,
                'product_id': product[0].id,
                'price_unit': item['price'],
                'product_uom_qty': item['quantity'],
                'ordered_qty': item['quantity'],
                'product_uom': product[0].uom_id.id,
                'valor_bruto': float(item['quantity']) * float(item['price'])
            }))

        schedule = datetime.strptime(
            venda['delivery_date_formatted'], '%Y-%m-%d')
        schedule += timedelta(hours=23)

        ids = []

        params = request.env['ir.config_parameter'].sudo()
        pick_type_env = request.env['stock.picking.type'].sudo(user)

        pick_order_type_id = int(params.get_param(
            'json_api.pick_type_order_id', default=False))
        picking_type_ref = pick_type_env.browse(pick_order_type_id)
        if picking_type_ref:
            src_id, dest_id = self._get_locations(
                user, partner, picking_type_ref)
            picking = request.env['stock.picking'].sudo(
                user).with_context(planned_picking=True).create({
                    'name': picking_type_ref.sequence_id.next_by_id(),
                    'scheduled_date': schedule,
                    'partner_id': partner[0].id,
                    'picking_type_id': picking_type_ref.id,
                    'move_lines': picking_items,
                    'location_id': src_id,
                    'location_dest_id': dest_id,
                    'origin': venda['order_id'],
                    'amount_total': self._calc_amount_total(picking_items),
                })
            move = request.env['stock.move'].sudo().search([
                ('picking_id', '=', picking.id)])
            move.write({'picking_type_id': picking_type_ref.id})

            ids.append(picking.id)

        pack_type_id = int(params.get_param(
            'json_api.pick_type_pack_id', default=False))
        packing_type_ref = pick_type_env.browse(pack_type_id)
        if packing_type_ref:
            src_id, dest_id = self._get_locations(
                user, partner, packing_type_ref)

            packing = request.env['stock.picking'].sudo(
                user).with_context(planned_picking=True).create({
                    'name': packing_type_ref.sequence_id.next_by_id(),
                    'scheduled_date': schedule,
                    'partner_id': partner[0].id,
                    'picking_type_id': packing_type_ref.id,
                    'move_lines': picking_items,
                    'location_id': src_id,
                    'location_dest_id': dest_id,
                    'origin': venda['order_id'],
                    'amount_total': self._calc_amount_total(picking_items),
                })
            move = request.env['stock.move'].sudo().search([
                ('picking_id', '=', packing.id)])
            move.write({'picking_type_id': packing_type_ref.id})

            ids.append(packing.id)

        outgoing_type_id = int(params.get_param(
            'json_api.pick_type_outgoing_id', default=False))
        requested_order_ref = pick_type_env.browse(outgoing_type_id)
        if requested_order_ref:
            src_id, dest_id = self._get_locations(
                user, partner, requested_order_ref)

            requested_order = request.env['stock.picking'].sudo(
                user).with_context(planned_picking=True).create({
                    'name': requested_order_ref.sequence_id.next_by_id(),
                    'scheduled_date': schedule,
                    'partner_id': partner[0].id,
                    'picking_type_id': requested_order_ref.id,
                    'move_lines': picking_items,
                    'location_id': src_id,
                    'location_dest_id': dest_id,
                    'origin': venda['order_id'],
                    'amount_total': self._calc_amount_total(picking_items),
                })
            move = request.env['stock.move'].sudo().search([
                ('picking_id', '=', requested_order.id)])
            move.write({'picking_type_id': requested_order_ref.id})

            ids.append(requested_order.id)

        return ids

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

from odoo.addons.delivery_easypost.models.easypost_request import EasypostRequest


old_prepare_picking = EasypostRequest._prepare_picking_shipments

def __prepare_picking_shipments_new(self, carrier, picking, is_return=False):
    shipment = old_prepare_picking(self, carrier, picking, is_return=is_return)
    if picking.shipping_payment_type == 'SENDER':
        return shipment

    payment_partner = None
    if picking.shipping_payment_type == 'RECEIVER':
        payment_partner = picking.partner_id
    elif picking.shipping_payment_type == 'THIRD_PARTY':
        payment_partner = picking.shipping_thirdparty_partner_id
    else:
        return shipment

    move_lines_with_package = picking.move_line_ids.filtered(lambda ml: ml.result_package_id)
    move_lines_without_package = picking.move_line_ids - move_lines_with_package
    if move_lines_without_package:
        options = {
            'order[shipments][0][options][payment][type]': picking.shipping_payment_type,
            'order[shipments][0][options][payment][account]': payment_partner.shipping_payment_account,
            'order[shipments][0][options][payment][country]': payment_partner.country_id.code,
            'order[shipments][0][options][payment][postal_code]': payment_partner.zip,
        }
        shipment.update(options)
    shipment_id = 0
    if move_lines_with_package:
        for _ in picking.package_ids:
            options = {
                'order[shipments][%d][options][payment][type]' % shipment_id: picking.shipping_payment_type,
                'order[shipments][%d][options][payment][account]' % shipment_id: payment_partner.shipping_payment_account,
                'order[shipments][%d][options][payment][country]' % shipment_id: payment_partner.country_id.code,
                'order[shipments][%d][options][payment][postal_code]' % shipment_id: payment_partner.zip,
            }
            shipment.update(self._options(shipment_id, carrier))
            shipment_id += 1

    return shipment

EasypostRequest._prepare_picking_shipments = __prepare_picking_shipments_new


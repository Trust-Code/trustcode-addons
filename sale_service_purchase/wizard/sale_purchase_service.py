# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class SalesPurchaseOrder(models.TransientModel):
    _name = 'sales.purchase.order'

    partner_id = fields.Many2one(
        'res.partner', 
        string="Vendor",
        required=True,
    )
    need_external_service = fields.Boolean(
        string="Need External Service"
    )
    
    @api.model
    def _get_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'),
                                ('warehouse_id.company_id', '=', company_id),])
        return types[0].id if types else False
    
    @api.multi
    def create_purchase_order(self):
        sale_order_id = self._context.get('active_id', False)
        sale_orders = self.env['sale.order'].browse(sale_order_id)
        purchase_order_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        for rec in self:
            order_ids = []
            if sale_orders.so_created:
                vals = rec._prepare_purchase_order(sale_orders, rec.partner_id)
                po = purchase_order_obj.create(vals)
                for line in sale_orders.order_line:
                    if not line.is_po_created:
                        if not line.product_id.type == 'service':
                            raise Warning(_('Some of the product found in the sales order that types is not service so the purchase order can not be created.'))
                        elif line.product_id.type == 'service' and not line.product_id.service_type == 'create_purchase_order':
                            raise Warning(_('Service Products are not set as track service with create purchase order option.'))
                        else:
                            order_line_vals = rec._prepare_purchase_order_line(po, line)
                            purchase_order_line = po_line_obj.create(order_line_vals)
                            order_ids.append(po.id)
                            line.is_po_created = True
            res = self.env.ref('purchase.purchase_form_action')
            res = res.read()[0]
            res['domain'] = str([('id','in',order_ids)])
        return res
    
    @api.multi
    def _prepare_purchase_order(self, sale_orders, partner):
        sale_order_id = sale_orders 
        fpos = self.env['account.fiscal.position'].with_context(\
                company_id=sale_order_id.company_id.id).get_fiscal_position(partner.id)
        res = {
            'partner_id': partner.id,
            'picking_type_id': self._get_picking_type(),
            'company_id': sale_order_id.company_id.id,
            'currency_id': partner.property_purchase_currency_id.id \
                            or self.env.user.company_id.currency_id.id,
            'origin': sale_order_id.name,
            'payment_term_id': partner.property_supplier_payment_term_id.id,
            'date_order': sale_order_id.date_order,
            'fiscal_position_id': fpos,
            'order_id': sale_order_id.id,
            'sale_order_id':sale_order_id.id
        }
        return res

    @api.multi
    def _prepare_purchase_order_line(self, po, line):
        taxes = line.product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == line.company_id.id)
        date_planned = datetime.today()
        seller = line.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=line.product_uom_qty,
            date=po.date_order,
            uom_id=line.product_id.uom_po_id)
        return {
            'product_qty': line.product_uom_qty,
            'product_id': line.product_id.id,
            'product_uom': line.product_id.uom_po_id.id,
            'price_unit': seller.price or 0.0,
            'date_planned': date_planned,
            'taxes_id': [(6, 0, taxes_id.ids)],
            'order_id': po.id,
            'name': line.name,
        }

    @api.multi
    def _prepare_purchase_requisition_line(self, pr, line):
        seller = line.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=line.product_uom_qty,
            date=pr.schedule_date,
            uom_id=line.product_id.uom_po_id)
        return {
            'product_qty': line.product_uom_qty,
            'qty_ordered': line.product_uom_qty,
            'product_id': line.product_id.id,
            'product_uom': line.product_id.uom_po_id.id,
            'price_unit': seller.price or 0.0,
            'schedule_date': fields.Datetime.now(),
            'requisition_id': pr.id,
            'name': line.name,
        }

    @api.multi
    def create_purchase_requisition(self):
        sale_order_id = self._context.get('active_id', False)
        sale_orders = self.env['sale.order'].browse(sale_order_id)
        PurchaseRequisition = self.env['purchase.requisition']
        PurchaseRequisitionLine = self.env['purchase.requisition.line']
        for rec in self:
            order_ids = []
            if sale_orders.so_created:
                vals = rec._prepare_purchase_order(sale_orders, rec.partner_id)
                vals.update({
                    'name': 'PR - {}'.format(sale_orders.name)
                })
                vals.pop('fiscal_position_id')
                pr = PurchaseRequisition.create(vals)
                for line in sale_orders.order_line:
                    if not line.is_po_created:
                        if not line.product_id.type == 'service':
                            raise Warning(_('Some of the product found in the sales order that types is not service so the purchase order can not be created.'))
                        elif line.product_id.type == 'service' and not line.product_id.service_type == 'create_purchase_order':
                            raise Warning(_('Service Products are not set as track service with create purchase order option.'))
                        else:
                            order_line_vals = rec._prepare_purchase_requisition_line(pr, line)
                            PurchaseRequisitionLine.create(order_line_vals)
                            order_ids.append(pr.id)
                            line.is_po_created = True
            res = self.env.ref('purchase_requisition.action_purchase_requisition')
            res = res.read()[0]
            res['domain'] = str([('id', 'in', order_ids)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

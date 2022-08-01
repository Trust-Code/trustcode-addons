# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Service & Make Purchase Order',
    'version': '1.0',
    'price': 40.0,
    'currency': 'EUR',
    'support': 'contact@probuse.com',
    'license': 'Other proprietary',
    'category': 'Sales',
    'summary': 'Allow us to create Purchase Order from Sales Order for product type services.',
    'description': """
   Allow us to create Purchase Order from Sales Order for product type services.     
Tags:
product type service
purchase order for type services product
sale services
Sales Service & Make Purchase Order
purchase services
create purchase order for service type product
product type service po
po services
raise order for service
purchase order type services
Sales Service - Purchase Order
create purchase order from sales order
purchase service from provider
purchase service from vendor
sale on service
sale with purchse
purchase
sale
purchase order
sales order
track service
track sales service
Is Need External Service
External Service
            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['sale', 'purchase'],
    'data': [
             'wizard/sales_purchase_order_view.xml',
             'views/sale_view.xml',
             'views/purchase_view.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

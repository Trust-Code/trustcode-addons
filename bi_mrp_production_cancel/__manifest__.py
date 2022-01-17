# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Manufacturing Order Cancel/Reverse in Odoo',
    'version': '13.0.0.7',
    'category': 'Manufacturing',
    'summary': 'Apps for allow to cancel Manufacturing Order cancel Manufacturing cancel order MO cancel Manufacturing reverse mrp cancel mrp order cancel reverse manufacturing order cancel stock reverse stock of MO production cancel order production order cancel' ,
    'description': """
    -Manufacturing Order reverse workflow, Manufacturing Order cancel, Manufacturing cancel,MO cancel, cancel Manufacturing order, Manufacturing reverse workflow, cancel MO reverse, cancel order, set to draft Manufacturing Order, cancel done Manufacturing Order, revese Manufacturing Order process, cancel done Manufacturing Order.reverse Manufacturing Order.
    mrp cancel with lot number
    mrp cancel with lot number
    mrp lot cancel order
    mrp serial cancel order
    manufacturing order cancel with lot number
    Manufacturing Order Cancel/reverse for goods in MRP production Odoo Apps
    manufacturing order cancel with serial number
    This Odoo apps use to cancel the MO after being done and again set it to "Draft" also update the quantity.
    This Odoo ap is useful for reverse complete MO when needed or any mistake done on manufacturing production Order. 
    This Odoo apps also manage proper reverse workflow for lot and serial number for raw materials and finished goods. 
    so if you are managing your products with lot or serial number tracking then don't worry this module take care of everything for reserve stock movement and quant calculation generated from the finished production order. If any accounting entry/journal entry transaction created from the Manufacturing order(With inventory valuation automated) those created journal entry is also deleted when 
    you cancel the done manufacturing/production order on Odoo ERP system.
    -Manufacturing reverse workflow, MRP production cancel order, prodcution order cancel, reverse production order, reverse MO,  Manufacturing cancel, Manufacturing orders cancel,Manufacture cancel, cancel Manufacture order, Manufacture reverse workflow, cancel MO reverse, cancel order, set to draft Manufacture Order, cancel done Manufacture Order, revese Manufacture Order process, cancel done Manufacture Order.reverse Manufacture Order.

-Forma de trabajo inversa de orden de fabricación, cancelación de orden de fabricación, cancelación de fabricación, cancelación de MO, cancelar orden de fabricación, flujo de trabajo inverso de fabricación, cancelar MO inversa, cancelar orden, establecer borrador de orden de fabricación, cancelar pedido de fabricación hecho, reverencia proceso de orden de fabricación, cancelar fabricación Orden de fabricación inversa.

     -Manufactura inversa flujo de trabajo, Fabricación cancelar, órdenes de fabricación cancelar, Fabricación cancelar, cancelar Fabricación orden, Fabricación flujo de trabajo inverso, cancelar MO inversa, cancelar orden, establecer borrador Orden de fabricación, cancelar hecho Fabricación orden, reverencia Fabricación Proceso de orden, cancelar hecho Orden de fabricación Orden de fabricación inversa.

-Fabrication Ordre inverse workflow, ordre de fabrication annuler, fabrication annuler, MO annuler, annuler ordre de fabrication, fabrication inverse workflow, annuler MO inverse, annuler commande, mis à brouillon ordre de fabrication, annuler fait Ordre de fabrication, revese processus de commande, annuler Ordre de fabrication inverse.

     -Fabrication inversée, Annulation de fabrication, Annulation de fabrication, Annulation de fabrication, Annulation de fabrication, Annulation de flux de travail, Annulation de MO, Annulation de commande, Mise en fabrication Commande, Annulation de commande, Revese Fabrication Commande, Annulation de commande Ordre de fabrication inverse.
    """,
    'price': 89,
    'currency': "EUR",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends': ['base', 'mrp','stock_account'],
    'data': ["views/mrp_production_views.xml",],
    'installable': True,
    'auto_install': False,
    'application': True,
    "images":['static/description/Banner.png'],
    "live_test_url":'https://youtu.be/FSyn6axMrhA',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

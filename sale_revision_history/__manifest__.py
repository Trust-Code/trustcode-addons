# -*- encoding: utf-8 -*-
{   # pylint: disable=C8101,C8103
    "name": "Sale Revision History",
    "version": "11.0.1.0.0",
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    "sequence": 0,
    "depends": ["sale", "sale_stock"],
    "category": "Sales,Invoicing",
    "complexity": "easy",
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    "description": """
Quotation sale revision history
    """,
    "data": [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizard/restore_items.xml',
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}

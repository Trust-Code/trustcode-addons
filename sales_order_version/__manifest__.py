# -*- coding: utf-8 -*-
# © 2016 Alessandro Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sales Order Versioning',
    'summary': """Módulo que cria um campo para controlar a versão da
            cotação enviada ao cliente.""",
    'description': "Controle de versão em Cotações",
    'version': '10.0.1.0.0',
    'category': 'Localisation',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': ['Danimar Ribeiro <danimaribeiro@gmail.com>',
                     'Mackilem Van der Laan Soares <mack.vdl@gmail.com>',
                     'Alessandro Martini <alessandrofmartini@gmail.com>',
                     ],
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_view.xml'
    ],
    'instalable': True
}

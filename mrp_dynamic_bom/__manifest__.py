# -*- coding: utf-8 -*-
# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'MRP Dynamic BoM',
    'description': "Permite lista de material dinamica para o MRP",
    'summary': "MRP Dynamic BoM",
    'version': '11.0.1.0.0',
    'category': "account",
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Johny Chen Jy <johnychenjy@gmail.com>',
    ],
    'depends': [
        'mrp',
    ],
    'data': [
        'views/mrp_dynamic_bom_views.xml',
        'security/ir.model.access.csv',
    ],
}

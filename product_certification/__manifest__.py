# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Certificação do Produto",

    'summary': """
        Cria campos para especificar entidade e número
        da certificação dos produtos""",
    'description': """
    """,
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_certification.xml',
        'views/product_template.xml',
    ],
}

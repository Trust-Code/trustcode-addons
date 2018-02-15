# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': "sale_variant_configurator",
    'summary': """
        Permite selecionar nas linhas da cotação o as variações do produto.""",
    'description': """""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Sale',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>',
        'Felipe Paloschi <paloschi.eca@gmail.com>'],
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],
}

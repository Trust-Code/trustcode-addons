# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Importação de BoM",

    'summary': """
        Permite a importação de BoM através de arquivos '.csv'.""",

    'description': """""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Purchase',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Johny Chen Jy <johnychenjy@gmail.com>',
    ],
    'depends': [
        'mrp'
    ],
    'data': [
        'wizard/bom_import_wizard.xml',
    ],
}

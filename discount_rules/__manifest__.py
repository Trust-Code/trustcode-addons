# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Regras de Desconto",
    'summary': """
        Este módulo aplica regras de desconto confome o grupo de usuário
    """,
    'description': """
        Este módulo aplica regras de desconto confome o grupo de usuário
    """,
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Sale',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Johny Chen Jy <johnychenjy@gmail.com>',
        'Danimar Ribeiro <danimaribeiro@gmail.com>'
    ],
    'depends': [
        'base', 'sale'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_config_settings_view.xml',
    ],
}

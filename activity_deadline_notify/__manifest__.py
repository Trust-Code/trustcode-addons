# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{   # pylint: disable=C8101,C8103,C7902
    'name': "Notificação de deadline das atividades",

    'summary': """
        Permite definir data e hora para atividades e envia uma notificação
        ao usuário quando estiver próximo da tarefa""",

    'description': """""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': ['base', 'mail', 'br_base', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/mail_activity.xml',
    ],
}

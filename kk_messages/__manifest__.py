# © 2020 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Ajuste de mensagens",
    'summary': """
        Ajuste de mensagens""",
    'description': """
        Ajusta algumas mensagens enviadas ao vendedor
    """,
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Danimar Ribeiro',
    ],
    'depends': ['mail', 'account', 'project'],
    'data': [
        'views/mail_templates.xml'
    ],
}

# © 2018 Danimar Ribeiro <danimaibeiro@gmail.com> Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{   # pylint: disable=C8101,C8103
    'name': 'Integração SMS Twilio',
    'version': '11.0.1.0.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author': 'Trustcode',
    'website': 'http://www.trustcode.com.br',
    'description': """
        Realiza a integração de SMS com Twilio""",
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'sms',
    ],
    'data': [
        'views/res_company.xml',
    ],
}

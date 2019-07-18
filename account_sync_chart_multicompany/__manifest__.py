# © 2019 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{   # pylint: disable=C8101,C8103
    'name': 'Synchronize Chart of Account',
    'version': '11.0.1.0.0',
    'category': 'Account',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'summary': """Syncronize chart of account between companies
    Created by Trustcode""",
    'website': 'https://www.trustcode.com.br',
    'support': 'comercial@trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>'
    ],
    'depends': [
        'account',
    ],
    'data': [
        'views/account.xml',
        'views/res_company.xml',
    ],
}

# © 2021 Danimar Ribeiro <danimaibeiro@gmail.com> Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{   # pylint: disable=C8101,C8103
    'name': 'Converte valores em dolar para reais no Site',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author': 'Trustcode',
    'website': 'http://www.trustcode.com.br',
    'description': """
        Converte valores em dolar para reais no Site""",
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'website_sale',
    ],
    'data': [
        'views/website_views.xml',
    ],
}

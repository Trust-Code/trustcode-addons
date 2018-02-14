# © 2015 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': 'Trustcode - Campos da Anvisa para Medicamentos',
    'description': 'Códigos da Anvisa',
    'summary': """
        Habilita alguns campos para venda de medicamentos e produtos
        cirurgicos
    """,
    'version': '10.0.1.0.0',
    'category': 'Stock',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'br_sale',
    ],
    'data': [
        'views/product_product.xml',
    ],
}

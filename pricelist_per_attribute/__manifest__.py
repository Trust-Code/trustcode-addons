{  # pylint: disable=C8101,C8103
    'name': 'Lista de Precos por Atributo',
    'version': '14.0.1.0.0',
    'category': 'account',
    'author': 'Trustcode',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'sale',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
    ],
}

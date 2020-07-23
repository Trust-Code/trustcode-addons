{   # pylint: disable=C8101,C8103
    'name': 'Modulo de Exemplo',
    'version': '12.0.1.0.0',
    'category': 'Account addons',
    'license': 'AGPL-3',
    'author': 'Trustcode',
    'website': 'http://www.trustcode.com.br',
    'description': """
        Cria movimento de estoque a partir de uma fatura com base na posição
         fiscal.""",
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pre_pedido.xml',
    ],
}

{   # pylint: disable=C8101,C8103
    'name': 'Modulo de Desenvolvimento CNAE',
    'version': '12.0.1.0.0',
    'category': 'addons',
    'author': 'Trustcode',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Renan Silveira <notfound.silveira@gmail.com>'
    ],
    'description': """Cria campos.""",
    'depends': [
        'contacts',
        'helpdesk',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'application': True,
}

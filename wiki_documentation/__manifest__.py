# © 2017 Mackilem Van der Laan, Trustcode
# © 2018 Danimar Ribeiro, Trustcode
# Part of Trustcode. See LICENSE file for full copyright and licensing details.


{
    'name': 'Wiki Documentation',
    'version': '13.0.1.0.1',
    'category': 'Document Management',
    'sequence': 5,
    'author': 'Trustcode',
    'license': 'OPL-1',
    'summary': """Design and create documentation for your employees and customers
    Created by Trustcode""",
    'website': 'https://www.trustcode.com.br',
    'support': 'comercial@trustcode.com.br',
    'price': '180',
    'currency': 'EUR',
    'contributors': [
        'Mackilem Van der Laan <mack.vdl@gmail.com>',
        'Danimar Ribeiro <danimaribeiro@gmail.com>'
    ],
    'depends': [
        'mail',
        'website',
    ],
    'data': [
        'security/documentation_security.xml',
        'wizard/wizard_review.xml',
        'views/documentation.xml',
        'views/documentation_portal.xml',
        'views/category.xml',
        'security/ir.model.access.csv',
        'views/snippets.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'application': True,
}

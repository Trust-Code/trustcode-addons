# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Gráficos customizados para Odoo',
    'summary': """Gráficos customizados para Odoo""",
    'description': """Gráficos customizados para Odoo - Mantido por Trustcode""",
    'version': '12.0.1.0.0',
    'category': 'Charts',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/charts.xml',
        'views/dashboards.xml',
    ],
    'instalable': True,
    'application': True,
}

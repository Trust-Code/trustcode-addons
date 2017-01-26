# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Trustcode Backup Simples',
    'summary': """Trustcode simples ferramenta de backup""",
    'version': '10.0.1.0.0',
    'category': 'Extra Tools',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    "description": """
        Este módulo permite configurar backup das bases
        de dados para rodar periodicamente, e integra com o Amazon S3
    """,
    'depends': [
        'base',
    ],
    'data': [
        "views/backup_s3.xml",
        "security/ir.model.access.csv"
    ],
    'application': True,
    'auto_install': False
}

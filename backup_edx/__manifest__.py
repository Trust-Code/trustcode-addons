# -*- coding: utf-8 -*-
# © 2017 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{   # pylint: disable=C8101,C8103
    'name': 'Trustcode Backup EDX',
    'summary': """Trustcode - Backup EDX""",
    'version': '11.0.1.0.0',
    'category': 'Extra Tools',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Johny Chen Jy<johnychenjy@gmail.com>',
    ],
    "description": """
        Este módulo permite configurar backup das bases
        de dados do EDX para rodar periodicamente, e integra com o Amazon S3
    """,
    'depends': [
        'base',
    ],
    'external_dependencies': {
        'python': [
            'fabric.api',
        ],
    },
    'data': [
        "views/backup_edx.xml",
        "security/ir.model.access.csv"
    ],
    'application': True,
    'auto_install': False
}

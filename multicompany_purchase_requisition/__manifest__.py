# © 2018 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{   # pylint: disable=C8101,C8103
    'name': 'Requisição de compras - Multi-empresas',
    'summary': """Requisição de compras - Multi-empresas""",
    'version': '11.0.1.0.0',
    'category': 'Extra Tools',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Johny Chen Jy <johnychenjy@gmail.com>'
    ],
    "description": """
        Requisição de compras - Multi-empresas
    """,
    'depends': [
        'purchase_requisition',
    ],
    'data': [
        "data/multicompany_purchase.xml",
        "views/purchase_multicompany.xml",
        "security/ir.model.access.csv",
        "wizard/wizard_multicompany_increment.xml",
        "views/purchase_multicompany_req.xml",
        "views/purchase_order.xml",
        "reports/report_romaneio.xml",
    ],
}

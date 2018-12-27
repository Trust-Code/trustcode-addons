# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Paraíso Stock",

    'summary': """
        Altera visualização do processo de entrega""",

    'description': """
        Bloqueia a impressão da ordem de separação;
        Atribui cores às linhas dos pedidos relacionando ao estoque;
        Atribui responsável pelas entregas.
    """,
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Marina Domingues <mgd.marinadomingues@gmail.com>',
    ],

    'depends': ['sale', 'stock'],
    'data': [
        "views/stock_move_view.xml",
        "views/stock_picking_view.xml",
        "views/res_partner_view.xml",
        "views/report.xml"
    ],

}

# -*- coding: utf-8 -*-
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Projeto por Linha de Venda',
    'description': 'Projeto por linha de venda',
    'summary': """ Cria um projeto para cada linha do pedido de venda """,
    'version': '11.0.1.0.0',
    'category': 'Project',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>'
    ],
    'depends': [
        'project', 'sale_timesheet'
    ],
    'data': [
        'views/product.xml'
    ],
}

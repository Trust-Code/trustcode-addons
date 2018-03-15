# © 2018 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': "Lista de materiais dinâmica",
    'summary': "Lista de materiais dinâmica - Baseado em regras",
    'description': "Lista de materiais dinâmica - Baseado em regras",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'MRP',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Danimar Ribeio <danimaribeiro@gmail.com>'
    ],
    'depends': [
        'mrp',
        'sale',
        'product_configurator'
    ],
    'data': [
        'views/project_task_type.xml'
    ],
}

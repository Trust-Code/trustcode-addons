# © 2015 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{  # pylint: disable=C8101,C8103
    'name': 'Controle de tempo das Tarefas',
    'description': 'Controle de tempo das Tarefas',
    'summary': """Automatiza a contagem de tempo nas tarefas
    de acordo com o estágio""",
    'version': '10.0.1.0.0',
    'category': 'Project',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Mackilem Van der Laan Soares <mack.vdl@gmail.com>',
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': [
        'project', 'hr_timesheet', 'hr_attendance'
    ],
    'data': [
        'views/project_task_view.xml',
    ],
}

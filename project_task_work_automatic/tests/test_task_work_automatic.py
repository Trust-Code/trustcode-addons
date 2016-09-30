# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.tests import common


class TestTaskTime(common.TransactionCase):

    def setUp(self):
        super(TestTaskTime, self).setUp()
        self.employee = self.env['res.users']\
            .browse(self.env.user.id).employee_ids[0]
        group_id = self.env['ir.model.data']\
            .get_object('base',  'group_hr_attendance')
        group_id.write({'users': [(4, self.env.user.id, None)]})
        self.stage_running = self.env.ref('project.project_tt_deployment')
        self.stage_running.count_time = True
        self.stage_stopping = self.env.ref('project.project_tt_deployment')
        self.stage_stopping.count_time = False
        self.reviewer_user = self.env['res.users'].create({
            'name': 'teste2',
            'login': 'teste',
            'company_id': self.env.user.company_id.id
        })
        self.reviewer_employee = self.env['hr.employee'].create({
            'name': 'teste2', 'user_id': self.reviewer_user.id
        })
        self.project = self.env['project.project'].create(
            {'name': 'Test Project'})
        self.task_one = self.env['project.task'].create({
            'name': 'task one',
            'project_id': self.project.id,
            "user_id": self.employee.id,
            "reviewer_id": self.reviewer_user.id
        })
        self.task_two = self.env['project.task'].create({
            'name': 'task two', 'project_id': self.project.id
        })

    def test_create_task_work(self):
        self.employee.attendance_action_change()

        self.assertEqual(self.employee.state, 'present',
                         'Não registrou corretamente entrada do usuário')

        self.assertEqual(len(self.task_one.work_ids), 0,
                         'Não deveria contar tempo nesta tarefa')

        self.assertEqual(len(self.task_two.work_ids), 0,
                         'Não deveria contar tempo nesta tarefa')

        self.task_one.stage_id = self.stage_running.id

        self.assertEqual(len(self.task_one.work_ids), 0,
                         'Não registrou o tempo na tarefa um')

        self.assertEqual(len(self.task_two.work_ids), 0,
                         'Não deveria contar tempo nesta tarefa')

    def test_time_locating(self):
        self.employee.attendance_action_change()

        self.reviewer_employee.attendance_action_change()

        self.project.user_id = self.reviewer_user.id

        self.task_one.stage_id = self.stage_running.id

        self.task_one.stage_stopping = self.stage_stopping.id

        self.assertNotEqual(self.task_one.work_ids.user_id.id,
                            self.env.user.id,
                            'Não deveria contar o tempo para o revisor')

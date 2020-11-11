from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FMT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FMT


class ProjectTask(models.Model):
    _inherit = "project.task"

    sprint_id = fields.Many2one("project.scrum.sprint", string="Sprint")

    @api.model
    def _read_group_sprint_id(self, present_ids, domain, **kwargs):
        project = self.env["project.project"].browse(
            self._resolve_project_id_from_context()
        )

        if project.use_scrum:
            sprints = (
                self.env["project.scrum.sprint"]
                .search([("project_id", "=", project.id)], order="sequence")
                .name_get()
            )
            return sprints, None
        else:
            return [], None

    _group_by_full = {
        "sprint_id": _read_group_sprint_id,
    }

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stages = super(ProjectTask, self)._read_group_stage_ids(stages, domain, order)
        if 'default_sprint_id' in self.env.context:
            return stages.sudo().search([], order=order)
        return stages

    @api.model
    def filter_current_sprint(self):
        sprint = self.env["project.scrum.sprint"]
        user = self.env.user
        view_type = "kanban,form,tree"
        team_id = user.scrum_team_id.id
        sprint_id = sprint.search(
            [("state", "=", "open"), ("scrum_team_id", "=", team_id)], limit=1
        )
        if sprint_id:
            value = {
                "domain": [("sprint_id", "=", sprint_id.id)],
                "context": {"default_sprint_id": sprint_id.id},
                "name": _("Current Sprint"),
                "view_type": "form",
                "view_mode": view_type,
                "res_model": "project.task",
                "view_id": False,
                "type": "ir.actions.act_window",
            }
        else:
            value = {
                "domain": [("id", "=", 0)],
                "name": _("Current Sprint"),
                "view_type": "form",
                "view_mode": view_type,
                "res_model": "project.task",
                "view_id": False,
                "type": "ir.actions.act_window",
                "help": "No sprint running.",
            }
        return value

    def action_sprint_backlog(self):
        team_id = self.env.user.scrum_team_id
        if team_id:
            value = {
                "domain": [("sprint_id", "in", (team_id.sprint_backlog_id.id, team_id.previous_backlog_id.id))],
                "context": {"default_sprint_id": team_id.sprint_backlog_id.id},
                "name": "Backlog",
                "view_mode": "tree,form",
                "res_model": "project.task",
                "type": "ir.actions.act_window",
            }
        else:
            value = {
                "domain": [("id", "=", 0)],
                "name": _("Current Sprint"),
                "view_mode": "tree,form",
                "res_model": "project.task",
                "view_id": False,
                "type": "ir.actions.act_window",
                "help": "No sprint running.",
            }
        return value


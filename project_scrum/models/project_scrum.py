import re
import logging
from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class ScrumSprint(models.Model):
    _name = "project.scrum.sprint"
    _description = "Project Scrum Sprint"
    _order = "date_start desc"

    name = fields.Char(string="Sprint Name", required=True)
    hide = fields.Boolean()
    date_start = fields.Date(
        string="Starting Date",
        default=fields.Date.today(),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_stop = fields.Date(
        string="Ending Date", readonly=True, states={"draft": [("readonly", False)]}
    )
    date_duration = fields.Integer(string="Duration(in hours)")
    description = fields.Text(string="Description")
    scrum_team_id = fields.Many2one("project.scrum.team", string="Team")
    task_ids = fields.One2many("project.task", inverse_name="sprint_id")
    review = fields.Html(
        string="Sprint Review",
        default="""
<ul>
<h5><li>What was the goal of this sprint?</li></h5><br/>
<h5><li>Has the goal been reached?</li></h5><br/><br/>
</ul>
    """,
    )
    retrospective = fields.Html(
        string="Sprint Retrospective",
        default="""
<ul>
<h5><li>What will you start doing in next sprint?</li></h5>
<br/><br/>
<h5><li>What will you stop doing in next sprint?</li></h5>
<br/><br/>
<h5><li>What will you continue doing in next sprint?</li></h5>
</ul>
    """,
    )
    progress = fields.Float(
        group_operator="avg",
        type="float",
        multi="progress",
        string="Progress (0-100)",
        help="Computed as: Total tasks / Total tasks done.",
    )
    effective_hours = fields.Float(
        multi="effective_hours",
        string="Effective hours",
        help="Computed using the sum of the task work done.",
    )
    planned_hours = fields.Float(
        multi="planned_hours",
        string="Planned Hours",
        help="Estimated time to do the task, usually set by the project \
        manager when the task is in draft state.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Executing"),
            ("cancel", "Cancelled"),
            ("done", "Done"),
        ],
        string="State",
        required=False,
        default="draft",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.user.company_id
    )

    def start_sprint(self):
        self.state = "open"

    def finish_sprint(self):
        for sprint in self:

            stage_cancelled = sprint.project_id.type_ids.filtered(lambda x: x.cancelled)
            if len(stage_cancelled) == 0:
                raise Warning("Configure um estágio para as tarefas canceladas")
            stage_done = sprint.project_id.type_ids.filtered(lambda x: x.closed)
            if len(stage_done) == 0:
                raise Warning(u"Configure um estágio para as tarefas concluídas")
            stages = sprint.project_id.type_ids.sorted(lambda x: x.sequence)
            points_done = 0
            for task in sprint.task_ids:
                if task.stage_id.closed:
                    points_done += task.points
                else:
                    if (
                        not task.stage_id.cancelled
                        and self.env.user.company_id.cancel_open_tasks_scrum
                    ):

                        task.sudo(
                            user=sprint.project_id.user_id
                        ).stage_id = stage_cancelled[0].id
                        task.copy(default={"stage_id": stages[0].id, "name": task.name})
            sprint.points_done = points_done
            sprint.state = "done"


class ProjectScrumTeam(models.Model):
    _name = "project.scrum.team"
    _description = "Scrum Team"

    name = fields.Char(string="Name", max_length=20, required=True)
    member_ids = fields.One2many(
        string="Members", comodel_name="res.users", inverse_name="scrum_team_id"
    )

    sprint_backlog_id = fields.Many2one("project.scrum.sprint")
    previous_backlog_id = fields.Many2one("project.scrum.sprint")

    @api.model
    def create(self, vals):
        team = super(ProjectScrumTeam, self).create(vals)
        backlog = self.env['project.scrum.sprint'].create(
            {"name": "Backlog - %s" % team.name, "hide": True},
        )
        team.sprint_backlog_id = backlog.id

        previous = self.env['project.scrum.sprint'].create(
            {"name": "Tarefas último sprint - %s" % team.name, "hide": True},
        )
        team.previous_backlog_id = previous.id
        return team


class ResUsers(models.Model):
    _inherit = "res.users"

    scrum_team_id = fields.Many2one("project.scrum.team", string="Scrum Team")

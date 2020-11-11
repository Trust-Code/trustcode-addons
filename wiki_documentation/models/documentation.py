# © 2018 Mackilem Van der Laan, Trustcode
# © 2018 Danimar Ribeiro, Trustcode
# Part of Trustcode. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta, datetime
from odoo.tools import html2plaintext
from odoo.addons.http_routing.models.ir_http import slug


class Documentation(models.Model):
    _name = 'doc.docs'
    _description = 'Module for Documentation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']

    def _compute_website_url(self):
        for doc in self:
            doc.website_url = "/my/document/%s" % (slug(doc))

    def _compute_bpmn_name(self):
        for doc in self:
            doc.bpmn_process_name = "%s.bpmn" % (doc.name)

    name = fields.Char(required="1")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string="Status",
        required=True,
        readonly=True,
        default="draft",
        track_visibility='onchange',
        selection=[
                ('draft', 'Draft'),
                ('review', 'Review'),
                ('approved', 'Approved'),
                ('approval', 'for Approval'),
        ],
    )
    type = fields.Selection(
        string="Type of Document",
        required=True,
        default="manual",
        selection=[
                ('manual', 'Manual'),
        ],
    )
    responsible_id = fields.Many2one(
        string="Responsible",
        comodel_name="res.partner",
        default=lambda self: self.env.user.partner_id.id,
        domain="[('is_company', '=', True)]",
        track_visibility='onchange',
    )
    enabled_partner_ids = fields.Many2many(
        string="Partners Enabled",
        comodel_name="res.partner",
        track_visibility='onchange',
        help="Partners enabled to use this documentation",
    )
    version = fields.Integer(
        string="Version",
        readonly=True,
        track_visibility='onchange',
        store=True,
    )
    category_id = fields.Many2one(
        string="Category",
        comodel_name="doc.category",
        ondelete='set null',
        track_visibility='onchange',
        help="Category of this document",
    )
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env['res.company'].
                                 _company_default_get('doc.docs'))
    next_review = fields.Date(
        string="Next Review",
        default=(datetime.today() + timedelta(days=+90)).date(),
        track_visibility='onchange',
    )
    description = fields.Html(
        string="Description",
        translate="True",
        track_visibility='onchange',
    )

    improvements = fields.Html(string="Last Submitted Improvements",
                               track_visibility='onchange')

    views = fields.Integer(string="Visualizações", default=0, readonly=True)
    likes = fields.Integer(string="Likes", default=0, readonly=True)
    dislikes = fields.Integer(string="Dislikes", default=0, readonly=True)
    teaser = fields.Char(
        string="Preview", compute='_compute_teaser', store=True)
    tag_ids = fields.Many2many(
        string="Tags",
        comodel_name="doc.tags"
    )

    @api.depends('description')
    def _compute_teaser(self):
        for doc in self:
            content = html2plaintext(doc.description).replace('\n', ' ')
            doc.teaser = content[:200] + '...'

    def button_approval(self):
        if self.state == "draft":
            self.version = 1
        self.state = "approved"
        self.improvements = False
        self.message_subscribe(self.enabled_partner_ids.ids)

    def button_review(self):
        if self.state == 'approved':
            self.copy({'active': False,
                       'name': '%s [deprecated]' % self.name,
                       'responsible_id': False,
                       'next_review': False})
            self.version = self.version + 1
            self.state = 'review'
            if self.category_id and self.category_id.days_review:
                days = self.category_id.days_review
                self.next_review = (datetime.today() + timedelta(days=+ days)).date()
            else:
                self.next_review = (datetime.today() + timedelta(days=+ 90)).date()
        elif self.state == 'approval':
            self.state = 'review'

    def message_get_suggested_recipients(self):
        recipients = super(
            Documentation, self).message_get_suggested_recipients()
        for partner in self.enabled_partner_ids:
            self._message_add_suggested_recipient(
                recipients, partner=partner)
        return recipients

    @api.onchange("category_id")
    def _onchange_category_id(self):
        if self.category_id and self.category_id.days_review:
            days_review = self.category_id.days_review
            self.next_review = datetime.today() + timedelta(days=+ days_review)

    @api.constrains("name", "version", "company_id")
    def _check_name_version(self):
        if self.search_count([('name', '=', self.name),
                              ('version', '=', self.version),
                              ('company_id', '=', self.company_id.id),
                              ('id', '!=', self.id)]):
            raise ValidationError(_("A document with this name already and "
                                    "version exists for this company"))
    def write(self, vals):
        if "website_published" in vals:
            if not self.env.user.has_group(
               'wiki_documentation.group_documentation_reviewer'):
                raise UserError('Você não tem permissão para publicar!')
        res = super(Documentation, self).write(vals)
        return res

    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        default['name'] = "%s (Copy)" % self.name
        return super(Documentation, self).copy(default)


class DocReviewWizard(models.TransientModel):
    _name = 'doc.review.wizard'

    improvements = fields.Html('Improvements')

    def request_approval(self):
        doc = self.env['doc.docs'].browse(self._context.get('active_id'))
        doc.write({'state': 'approval',
                   'improvements': self.improvements})
        return {'type': 'ir.actions.act_window_close'}

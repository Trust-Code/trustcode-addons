# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ActivityChecklist(models.Model):
    _name = 'activity.checklist'

    name = fields.Char('Nome')
    checklist_item_ids = fields.One2many(
        'activity.checklist.item', 'checklist_id', 'Atividades')
    # owner
    res_id = fields.Integer('Related Document ID', index=True, required=True)
    res_model_id = fields.Many2one(
        'ir.model', 'Related Document Model',
        index=True, ondelete='cascade', required=True)
    res_model = fields.Char(
        'Related Document Model',
        index=True, related='res_model_id.model', store=True, readonly=True)
    res_name = fields.Char(
        'Document Name', compute='_compute_res_name', store=True,
        help="Display name of the related document.", readonly=True)
    is_done = fields.Boolean('Completo', compute="_compute_is_done")

    @api.multi
    def _compute_is_done(self):
        for checklist in self:
            checklist.is_done = False
            if all(item.is_done for item in checklist.checklist_item_ids):
                checklist.is_done = True

    @api.model
    def create(self, values):
        # already compute default values to be sure those
        # are computed using the current user
        values_defaults = self.default_get(self._fields.keys())
        values_defaults.update(values)
        model = self.env['ir.model'].search(
            [('model', '=', values_defaults['res_model'])], limit=1)
        values_defaults.update({
            'res_model_id': model.id,
            'res_name': model.name
        })
        return super(ActivityChecklist, self.sudo()).create(
            values_defaults)


class ActivityChecklistItem(models.Model):
    _name = 'activity.checklist.item'

    name = fields.Char('Nome')
    checklist_id = fields.Many2one('activity.checklist', 'Checklist')
    is_done = fields.Boolean('Pronto')

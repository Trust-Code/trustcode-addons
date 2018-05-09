# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pytz
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError


class ActivityChecklist(models.Model):
    _name = 'activity.checklist'

    name = fields.Char('Nome')
    checklist_item_ids = fields.One2many(
        'activity.checklist.item', 'checklist_id', 'Atividades')
    # owner
    res_id = fields.Integer('Related Document ID', index=True)
    res_model_id = fields.Many2one(
        'ir.model', 'Related Document Model',
        index=True, ondelete='cascade')
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
        vals = self.default_get(self._fields.keys())
        vals.update(values)
        if vals.get('res_model'):
            if any(self.env['activity.checklist'].search(
                    [('res_id', '=', vals['res_id']),
                     ('res_model', '=', vals['res_model'])])):
                raise UserError('Já existe uma checklist associada a este\
                    objeto.')
            model = self.env['ir.model'].search(
                [('model', '=', vals['res_model'])], limit=1)
            vals.update({
                'res_model_id': model.id,
                'res_name': model.name
            })
        return super(ActivityChecklist, self.sudo()).create(
            vals)

    def mark_checklist_done(self):
        res_obj = self.env[self.res_model].browse(self.res_id)
        if not self.is_done:
            raise UserError('Você não pode finalizar uma checklist que contém\
                itens não finalizados')
        tz = pytz.timezone(self.env.user.partner_id.tz) or pytz.utc
        dt = datetime.utcnow()
        dt = pytz.utc.localize(dt).astimezone(tz)
        message = ('Checklist finalizada por {} em {}!<br /> Itens: <br /><ul>'
                   .format(self.env.user.name, dt.strftime(
                       '%d-%m-%Y %H:%M:%S')))
        for item in self.checklist_item_ids:
            message += '<li>{}</li>'.format(item.name)
        message += '</ul>'
        res_obj.message_post(message)
        self.unlink()
        return


class ActivityChecklistItem(models.Model):
    _name = 'activity.checklist.item'

    name = fields.Char('Nome', required=True)
    checklist_id = fields.Many2one('activity.checklist', 'Checklist')
    is_done = fields.Boolean('Pronto')

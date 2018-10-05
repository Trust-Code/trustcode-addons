from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
   
    current_revision_id = fields.Many2one('sale.order','Current revision',readonly=True,copy=True)
    old_revision_ids = fields.One2many('sale.order','current_revision_id','Old revisions',readonly=True,context={'active_test': False})
    revision_number = fields.Integer('Revision',copy=False)
    unrevisioned_name = fields.Char('Order Reference',copy=True,readonly=True)
    active = fields.Boolean('Active',default=True,copy=True)    
    
    @api.model
    def create(self, vals):
        if 'unrevisioned_name' not in vals:
            if vals.get('name', 'New') == 'New':
                seq = self.env['ir.sequence']
                vals['name'] = seq.next_by_code('sale.order') or '/'
            vals['unrevisioned_name'] = vals['name']
        return super(SaleOrder, self).create(vals)
    
    @api.multi
    def action_revision(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        self.with_context(sale_revision_history=True).copy()
        self.write({'state': 'draft'})
        self.order_line.write({'state': 'draft'})
        self.mapped('order_line').write(
            {'sale_line_id': False})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
        
    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('sale_revision_history'):
            prev_name = self.name
            revno = self.revision_number
            self.write({'revision_number': revno + 1,'name': '%s-%02d' % (self.unrevisioned_name,revno + 1)})
            defaults.update({'name': prev_name,'revision_number': revno,'active': False,'state': 'cancel','current_revision_id': self.id,'unrevisioned_name': self.unrevisioned_name,})
        return super(SaleOrder, self).copy(defaults)




    
   

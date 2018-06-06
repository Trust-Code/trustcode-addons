from odoo import fields, models, api


class AdditionalInfoWizard(models.TransientModel):
    _name = 'additional.info.wizard'

    additional_info = fields.Text('Additional Info')

    @api.multi
    def action_confirm(self):
        print('batata')

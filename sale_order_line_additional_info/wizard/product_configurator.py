from odoo import models, api


class ProductConfigurator(models.TransientModel):
    _inherit = "product.configurator"

    @api.multi
    def action_config_done(self):
        super(ProductConfigurator, self).action_config_done()

        wizard_action = {
            'type': 'ir.actions.act_window',
            'res_model': 'additional.info.wizard',
            'name': "Configure Product",
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }
        return wizard_action

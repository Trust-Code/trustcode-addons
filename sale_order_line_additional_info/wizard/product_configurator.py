from odoo import models


class ProductConfigurator(models.TransientModel):
    _inherit = "product.configurator"

    def action_config_done(self):
        super(ProductConfigurator, self).action_config_done()
        import ipdb
        ipdb.set_trace()
        wizard_action = {
            'type': 'ir.actions.act_window',
            'res_model': 'additional.info.wizard',
            'name': "Configure Product",
            'view_mode': 'form',
            'context': dict(
                self.env.context,
                wizard_id=self.id,
            ),
            'target': 'new',
            'res_id': self.id,
        }
        return wizard_action

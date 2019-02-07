from odoo import fields, models


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    asset_number = fields.Char(
        related='asset_id.asset_number',
        string='Asset Number')

    project_id = fields.Many2one('project.project', string="Project")

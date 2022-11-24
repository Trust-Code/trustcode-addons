from odoo import models, fields, api, _

class CustomSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    group_send_sms = fields.Boolean(string="Direct WhatsApp Message", implied_group='odoo_whatsapp_integration.group_send_sms')
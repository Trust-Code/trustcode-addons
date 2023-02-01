#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_log = logging.getLogger(__name__)

class VideoAttachmentWizard(models.TransientModel):
    _name = "video.attachment.wizard"
    _description = "Video Attachment Wizard"

    attachment = fields.Binary(string="Attachment", required=True)
    name = fields.Char(string='Name')

    def add_video_attachment(self):
        modelName = self._context.get('active_model')
        modelId = self._context.get('active_id')
        attachment = self.env['ir.attachment'].sudo()
        datas = self.attachment
        vals = {
            'name': self.name,
            'datas': datas,
            'res_model': modelName,
            'res_id': modelId,
            'type': 'binary',
            'db_datas': self.name,
            'res_name': self.name,
        }
        mimetype = attachment._compute_mimetype(vals)
        allowed_types = self.env['website.slide.video'].get_allowed_formats()
        if not allowed_types.get(mimetype, False):
            raise UserError(_("Only allowed video formats can be uploaded."))

        file_size = allowed_types[mimetype] * 1024 * 1024
        given_file_size = len(base64.b64decode(datas))

        if file_size < given_file_size:
            raise UserError(_("video size less than %sMb can be uploaded and found %sMB.", allowed_types[mimetype], round(len(self.attachment)/(1024 * 1024), 2)))

        vals['mimetype'] = mimetype
        res = attachment.create(vals)
        slide = self.env['slide.slide'].browse(modelId)
        slide.slide_attachment = res.id

        return True

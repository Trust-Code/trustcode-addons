# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################
import base64
import filetype
from odoo import api, fields, models, _
from logging import getLogger
from odoo.exceptions import UserError
from odoo.http import request
from werkzeug import urls
from odoo.addons.http_routing.models.ir_http import url_for


_logger = getLogger(__name__)
class Slide(models.Model):
    _inherit = 'slide.slide'

    fname = fields.Char(string='Name',default='file_attachment')
    attachment = fields.Binary(string="Attachment")
    slide_attachment = fields.Many2one('ir.attachment', help="Video/Document")
    document_type = fields.Selection([('url', 'URL'), ('binary', 'File')],
                            string='Document Type', required=True, default='url', change_default=True,
                            help="You can either upload a file from your computer or copy/paste an internet link to your file.")
    
    @api.onchange('attachment')
    def add_media_attachment(self):
        if self.slide_type == 'video' and not isinstance(self.attachment,bool):
            attachment = self.env['ir.attachment'].sudo()   
            datas = self.attachment           
            vals = {
                'name': self.fname,
                'datas': datas,
                'res_model': self._name,
                'type': 'binary'  
            }
            allowed_types = self.env['website.slide.video'].get_allowed_formats()
            raw = base64.b64decode(datas)
            filetype_obj = filetype.guess(raw)
            if filetype_obj:
                mimetype = filetype_obj.mime
            else:
                mimetype = ''
            
            if  not allowed_types.get(mimetype, False):
                raise UserError(_("Only allowed video formats can be uploaded."))

            file_size = allowed_types[mimetype] * 1024 * 1024
            given_file_size = len(base64.b64decode(datas))

            if file_size < given_file_size:
                raise UserError(_("video size less than %sMb can be uploaded and found %sMB.", allowed_types[mimetype], round(len(self.attachment)/(1024 * 1024), 2)))
            vals['mimetype'] = mimetype
            res = attachment.create(vals) 
            self.slide_attachment = res.id
            
            



    @api.model
    def create(self, values):
        channel_id = self._context.get('default_channel_id')
        if channel_id:
            values['channel_id'] = channel_id
        if values.get('document_type') == 'binary':
            values['slide_type'] = 'video'
        res = super(Slide, self).create(values)
        return res

    def write(self, values):
        if values.get('document_type') == 'binary':
            values['slide_type'] = 'video'
        res = super(Slide, self).write(values)
        return res

    @api.onchange('document_type')
    def remove_link(self):
        self.url = ''
        self.datas = ''
        self.attachment = False
        self.image_1920 = False
        self.slide_attachment = False

    @api.onchange('url')
    def remove_attachment_link(self):
        self.slide_attachment = False

    @api.onchange('slide_type')
    def change_doc_type(self):
        if self.slide_type != 'video':
            self.document_type = 'url'
            
    def _compute_embed_code(self):
        base_url = request and request.httprequest.url_root or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url[-1] == '/':
            base_url = base_url[:-1]
            
        for record in self:
            if record.datas and (not record.document_id or record.slide_type in ['document', 'presentation']):
                slide_url = base_url + url_for('/slides/embed/%s?page=1' % record.id)
                
                record.embed_code = '<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (slide_url, 315, 420)
            elif record.slide_type == 'video' and record.document_id and record.document_type=='url':
                if not record.mime_type:
                    # embed youtube video
                    query = urls.url_parse(record.url).query
                    
                    query = query + '&theme=light' if query else 'theme=light'
                    record.embed_code = '<iframe src="//www.youtube-nocookie.com/embed/%s?%s" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id, query)
                else:
                    # embed google doc video
                    record.embed_code = '<iframe src="//drive.google.com/file/d/%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
                    
            
            else:              
                record.embed_code = False
                

class WebsiteSlides(models.Model):
    _name = "website.slide.video"
    _description = "Website Slide Video"

    name = fields.Char("MIME Types",help="Write extension of videos allowed")
    is_active = fields.Boolean("Is Active")
    website_id = fields.Many2many("website")
    file_size = fields.Integer("Size in Mb",help='Make sure max size is allowed in your webserver(ex:-nginx) then only this limit will work.',default=15)

    def get_allowed_formats(self):
        allowed_format = {}
        website_id = self.env['website'].get_current_website()
        records = self.sudo().search([('is_active', '=', True)])
        for record in records:
            if not record.website_id or (website_id.id in record.website_id.ids):
                allowed_format.update({'video/'+record.name:record.file_size})
        return allowed_format

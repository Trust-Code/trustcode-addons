from odoo.http import route, request, Controller, Response
from werkzeug.exceptions import NotFound
import base64
import logging
_log = logging.getLogger(__name__)


class VideoController(Controller):

    @route('/get_video/<int:attachment_id>', type='http', auth='public', website=True)
    def get_video(self, attachment_id, **post):
        try:
            accept = request.httprequest.headers.get('Accept')
            if accept and 'video/*' in accept or accept == '*/*':
                attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
                if attachment and 'video' in attachment.mimetype:
                    data = base64.standard_b64decode(attachment["datas"])
                    mimetype = attachment.mimetype
                    headers = [('Content-Type', mimetype),('Accept-Ranges', 'bytes')]
                    data_len = len(data)
                    status = 200
                    if request.httprequest.range:
                        contentrange = request.httprequest.range.make_content_range(data_len)
                        if contentrange.stop < data_len:
                            status = 206
                            headers.append(('Content-Range','bytes %s-%s/%s' % (str(contentrange.start), str(contentrange.stop), str(data_len))))
                        elif contentrange.stop > data_len:
                            status = 416
                            data = ''
                    return Response(data, status=status, headers=headers, content_type=mimetype)
            else:
                raise NotFound()
        except Exception:
            raise NotFound()

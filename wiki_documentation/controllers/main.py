# © 2018 Mackilem Van der Laan, Trustcode
# © 2018 Danimar Ribeiro, Trustcode
# Part of Trustcode. See LICENSE file for full copyright and licensing details.


from odoo import http
from odoo.http import request


class DocumentationController(http.Controller):

    @http.route(['/my/documents'], type='http', auth='public', website=True, track=True)
    def trustcode_my_documents(self, categoria=None, search=None, tag=None,
                               **kwargs):
        domain = []
        if categoria:
            domain += [('category_id', '=', int(categoria))]
        if search:
            domain += ['|', ('name', 'ilike', search),
                       ('description', 'ilike', search)]
        if tag:
            domain += [('tag_ids', 'in', [int(tag)])]

        documents = request.env['doc.docs'].search(domain)
        categories = request.env['doc.category'].search([], order='name asc')
        tags = request.env['doc.tags'].search([], order='name asc')
        recentes = vistos = request.env['doc.docs'].browse()
        if not search and not categoria:
            recentes = request.env['doc.docs'].search(
                [], limit=5, order='write_date desc')
            vistos = request.env['doc.docs'].search(
                [], limit=5, order='views desc')
        vals = {
            'documents': documents,
            'page_name': 'documents',
            'categories': categories,
            'tags': tags,
            'search': search,
            'categoria': int(categoria or '0'),
            'tag': int(tag or '0'),
            'recentes': recentes,
            'vistos': vistos,
        }
        return request.render(
            "wiki_documentation.portal_my_documents", vals)

    @http.route(['/my/document/<model("doc.docs"):document>'], type='http',
                auth='public', website=True, track=True)
    def trustcode_document(self, document, **kwargs):
        categories = request.env['doc.category'].search([], order='name asc')
        tags = []
        domain = [('tag_ids', 'in', document.tag_ids.ids),
            ('id', '!=', document.id),
            ('website_published', '=', True)]
        related_documents = request.env['doc.docs'].search(
            domain, limit=5, order='views desc')
        vals = {
            'doc': document,
            'page_name': 'document',
            'categories': categories,
            'related_documents': related_documents,
        }
        request.env.cr.execute('update doc_docs set views = %s where id = %s',
                               (document.views + 1, document.id))
        return request.render(
            "wiki_documentation.portal_my_document", vals)

    @http.route(['/document/like/<model("doc.docs"):document>'],
                type='http', auth='public')
    def trustcode_my_document_like(self, document):
        request.env.cr.execute('update doc_docs set likes = %s where id = %s',
                               (document.likes + 1, document.id))
        message = 'Gostei :+1 por %s' % request.env.user.login
        document.sudo().message_post(body=message)

    @http.route(['/document/dislike/<model("doc.docs"):document>'],
                type='http', auth='public')
    def trustcode_my_document_dislike(self, document):
        request.env.cr.execute(
            'update doc_docs set dislikes = %s where id = %s',
            (document.dislikes + 1, document.id))
        message = 'Não gostei :-1 por %s' % request.env.user.login
        document.sudo().message_post(body=message)

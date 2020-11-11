# © 2017 Mackilem Van der Laan, Trustcode
# © 2018 Danimar Ribeiro, Trustcode
# Part of Trustcode. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class DocumentationTags(models.Model):
    _name = 'doc.tags'
    _description = 'Documentation Tags'

    name = fields.Char(string="Name", size=50)
    color = fields.Integer()


class DocumentationCategory(models.Model):
    _name = 'doc.category'
    _description = 'Category of Documentation'

    name = fields.Char(string="Name")
    icon = fields.Char(string="Font Awesome Icon")
    image = fields.Binary("Imagem", attachment=True,
        help="This field holds the image used as avatar for this category")
    description = fields.Char(string="Descrição Web")
    sequence = fields.Integer()
    group_ids = fields.Many2many(
        "res.groups", string="Restricted Groups")
    days_review = fields.Integer(
        "Days to Review", default=45,
        help="Days to review docs with this category")
    document_ids = fields.One2many('doc.docs', 'category_id')

# © 2016 Wellysson Melo, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class LibraryBooks(models.Model):
    _name = 'library.books'

    name = fields.Char('Title', size=150, required='1')
    author_id = fields.Many2one('res.partner', string='Author')
    publishing_company_id = fields.Many2one('res.partner', string='Publishing Company', required='1')
    original_publishing_company = fields.Char('Publishing Company(Orig. Name)', size=150, help="publishing company's original name")
    edition = fields.Char('Edition', help="Edition Number", size=2, required='1')
    release_year = fields.Integer('Release Year')
    chapters = fields.Integer('Chapters')
    pages = fields.Integer('Pages')
    original_publication_id = fields.Many2one('library.books.publication.type', string='Original Pub.')
    doi = fields.Char('DOI', size=150, help="Digital Object Identifier")
    request_date_doi = fields.Date('Request Date DOI')
    license_id = fields.Many2one('library.books.license', string='License')
    is_paid = fields.Boolean('Paid')
    meeting_id = fields.Many2one('library.books.meeting', string='Meeting')
    sbid = fields.Char('SBID', size=20)
    isbn = fields.Char('ISBN', size=20, help="National Standard Book Number")
    eisbn = fields.Char('eISBN', size=20)
    value_usd = fields.Float('USD', help="United States Dollar")
    value_br = fields.Float('R$', help="Real (Brazilian Coin)")
    access_type_id = fields.Many2one('library.books.access.type', string='Access')
    series_collection_id = fields.Many2one('library.books.series.collection', string='Series/Colection')
    with_panding = fields.Boolean('With Panding')
    has_parts = fields.Boolean('Has Parts?')
    is_published = fields.Boolean('Published')
    publication_date = fields.Date('Publication Date')
    comments = fields.Text('Comments')
    feedback_type_id = fields.Many2one('library.books.feedback.type', string='Feedback Type')
    files_format_id = fields.Many2one('library.books.files.format', string='Files Format')
    has_printed = fields.Boolean('Has Printed')
    is_digitized = fields.Boolean('Digitized')
    is_backoffice = fields.Boolean('Backoffice')
    pdf_split = fields.Selection([('not_applicable', 'Not Applicable'), ('ok', 'OK'), ('produce', 'Produce')], string='PDF Split')
    cover_pages = fields.Selection([('ok', 'OK'), ('produce', 'Produce')], string='Cover Pages')
    is_epub_published = fields.Boolean('ePUB Published')
    epub_version = fields.Boolean('ePUB Version')
    provider_id = fields.Many2one('res.partner', string='Provider')
    value_usd_production = fields.Float('USD', help="Production Cost(USD - United States Dollar)")
    value_br_production = fields.Float('R$', help="Production Cost (Real - Brazilian Coin)")
    eisbn_order_lot = fields.Char('eISBN Order Lot')
    send_date = fields.Date('Send Date')
    prevision_date = fields.Date('Prevision Date')
    delivery_date = fields.Date('Delivery Date')
    technical_verif_date = fields.Date('Date')
    technical_verif_user = fields.Many2one('res.partner', string='User')
    content_verif_date = fields.Date('Date')
    content_verif_user = fields.Many2one('res.partner', string='User')
    kindle_verif_date = fields.Date('Date')
    kindle_verif_user = fields.Many2one('res.partner', string='User')
    ipad_verif_date = fields.Date('Date')
    ipad_verif_user = fields.Many2one('res.partner', string='User')
    pdf_publication_send_date = fields.Date('Send Date')
    pdf_publication_update_date = fields.Date('Update Date')
    epub_publication_send_date = fields.Date('Send Date')
    epub_publication_update_date = fields.Date('Update Date')
    amaz_publication_send_date = fields.Date('Send Date')
    amaz_publication_update_date = fields.Date('Update Date')
    kobo_publication_send_date = fields.Date('Send Date')
    kobo_publication_update_date = fields.Date('Update Date')
    google_epub_publication_send_date = fields.Date('Send Date')
    google_epub_publication_update_date = fields.Date('Update Date')
    google_pdf_publication_send_date = fields.Date('Send Date')
    google_pdf_publication_update_date = fields.Date('Update Date')
    bibliomundi_send_date = fields.Date('Send Date')
    bibliomundi_update_date = fields.Date('Update Date')
    openlibrary_send_date = fields.Date('Send Date')
    openlibrary_update_date = fields.Date('Update Date')
    ebsco_eds_send_date = fields.Date('Send Date')
    ebsco_eds_update_date = fields.Date('Update Date')
    central_ebooks_send_date = fields.Date('Send Date')
    central_ebooks_update_date = fields.Date('Update Date')
    proquest_send_date = fields.Date('Send Date')
    proquest_update_date = fields.Date('Update Date')
    exlibris_send_date = fields.Date('Send Date')
    exlibris_update_date = fields.Date('Update Date')
    jstor_send_date = fields.Date('Send Date')
    jstor_update_date = fields.Date('Update Date')
    doab_send_date = fields.Date('Send Date')
    doab_update_date = fields.Date('Update Date')
    oclc_send_date = fields.Date('Send Date')
    oclc_update_date = fields.Date('Update Date')
    kbart_file = fields.Binary('KBART')
    kbart_filename = fields.Char('KBART file name')
    responsible_provider = fields.Many2one('res.partner', string="Responsible Provider for Marking")
    markup_lot = fields.Char('Markup Lot')
    volume = fields.Char('Volume')
    references_number = fields.Integer('References Number')
    send_date_markup = fields.Date('Send Date for Markup')
    markup_receipt_date = fields.Date('Markup Receipt Date')
    highlights_date = fields.Date('Highlights Date')
    synopsis_reference = fields.Text('Reference')
    synopsis = fields.Text('Synopsis')
    keywords = fields.Text('Keywords')
    bisac = fields.Char('BISAC', size=150)
    bisac_complem = fields.Char('BISAC Complement', size=150)

class LibraryBooksMeeting(models.Model):
    _name = 'library.books.meeting'

    name = fields.Char('Name', size=50, required='1')

class LibraryBooksPublicationType(models.Model):
    _name = 'library.books.publication.type'

    name = fields.Char('Name', size=50, required='1')

class LibraryBooksLicense(models.Model):
    _name = 'library.books.license'

    name = fields.Char('Name', size=150, required='1')

class LibraryBooksAccessType(models.Model):
    _name = 'library.books.access.type'

    name = fields.Char('Name', size=50, required='1')

class LibraryBooksSeriesCollection(models.Model):
    _name = 'library.books.series.collection'

    name = fields.Char('Name', size=150, required='1')

class LibraryBooksFeedbackType(models.Model):
    _name = 'library.books.feedback.type'

    name = fields.Char('Name', size=50, required='1')

class LibraryBooksFilesFormat(models.Model):
    _name = 'library.books.files.format'

    name = fields.Char('Name', size=50, required='1')


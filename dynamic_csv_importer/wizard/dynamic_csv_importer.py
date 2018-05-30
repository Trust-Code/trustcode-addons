from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import csv
import io


class DynamicCsvImport(models.TransientModel):
    _name = "dynamic.csv.import"

    model_id = fields.Many2one(
        'ir.model', string="Model", required=True)

    csv_file = fields.Binary(string='CSV file', required=True)
    extra = fields.Boolean()

    csv_delimiter = fields.Char(
        string='Delimiter', size=3, required=True, default=',')

    has_quote_char = fields.Boolean(
        string=u'Has Quotation Char?', default=True)
    csv_quote_char = fields.Char(
        string=u'Quotation Char', size=3, default='"')

    table_html = fields.Html(readonly=True, store=True)
    coluna_ids = fields.One2many(
        'dynamic.import.line', 'importer_id', string="Columns")

    import_success = fields.Boolean(default=False)

    @api.onchange('csv_file', 'has_quote_char', 'csv_quote_char',
                  'model_id', 'csv_delimiter')
    def _onchange_csv_file(self):
        self._generate_table()

    @api.multi
    def action_import(self):
        # All dat CSV Files stuff
        if not self.csv_file:
            raise UserError(_('No csv file selected!'))

        csv_file = base64.b64decode(self.csv_file)
        csvfile = io.StringIO(csv_file.decode('utf-8'))

        if not self.has_quote_char:
            csv_lines = csv.DictReader(
                csvfile, delimiter=str(self.csv_delimiter))
        else:
            if not self.csv_quote_char:
                raise UserError(_(u'Quotation char missing. Please select \
an Quotation character before proceeding.'))
            csv_lines = csv.DictReader(
                csvfile, delimiter=str(self.csv_delimiter),
                quotechar=self.csv_quote_char)

        identification_lines = self.coluna_ids.filtered(
            lambda x: x.identifier)
        if not identification_lines:
            raise UserError(_(u'No identification lines! Please select at least one\
 identification line before proceeding.'))

        data_lines = self.coluna_ids.filtered(
            lambda x: x.domain_string and not x.identifier)
        if not data_lines:
            raise UserError(_(u'No import lines with domain detected! Please \
select an Odoo field or put a domain on at least one line before proceeding.'))

        model_id = self.env[self.model_id.model]

        # pre load all external references before iterating the csv lines
        obj_dict = self._get_object_dict(
            identification_lines + data_lines, model_id)

        errors = []
        lista = []

        # create/update object for each csv line
        for index, line in enumerate(csv_lines):
            search_domain = []

            for ident in identification_lines:
                search_domain.append(
                    (ident.domain_string, '=', line[ident.name]))

            object_ids = model_id.search(search_domain)

            has_match_obj = True if object_ids else False

            # Index is used for error message
            vals, error = self._prepare_vals(
                line, data_lines, obj_dict, has_match_obj=has_match_obj,
                line_index=index)
            if error:
                errors.append(error)
            # There's already errors on it... no need to proceed
            elif errors:
                continue
            lista.append((object_ids, vals, line))

        if errors:
            raise UserError(errors)

        for item in lista:
            object_ids = item[0]
            vals = item[1]
            line = item[2]
            if object_ids:
                for obj in object_ids:
                    obj.write(vals)
            else:
                ident_vals = self._prepare_vals(
                    line, identification_lines, obj_dict, has_match_obj=False)
                vals.update(ident_vals[0])
                # 'id' is needed for External ID creation
                if 'id' not in vals:
                    vals['id'] = line[identification_lines[0].name]

                fields = list(vals.keys())
                values = list(vals.values())
                res = model_id.load(fields, [values])

                if res['messages'] and res['messages'][0]['type'] == 'error':
                    raise UserError(res['messages'][0]['message'])
        self.import_success = True

        # Maintaining wizard open
        return {
            "type": "set_scrollTop",
        }

    def _get_object_dict(self, lines, model_id):
        """Returns a dict of objects identified by the
        domain contained in each line in lines
        """
        obj_dict = {}
        for line in lines:
            domain = line.domain_string.split('.')
            obj = model_id
            if len(domain) > 1:
                obj = obj[domain[0]]
                for item in domain[1:-1]:
                    obj = obj[item]
            obj_dict[line.id] = obj
        return obj_dict

    def _prepare_vals(self, line, data_lines, obj_dict, has_match_obj,
                      line_index=0):
        """
        :param line: dict with the csv line values
        :param data_lines: dynamic.import.line objects
        :param obj_dict: dict with all external references
        :param has_match_obj: boolean. Means if there's another
        register with the same identification data
        :param line_index: number of the line in csv file
        """
        vals = {}
        error = ''
        for data in data_lines:
            data_domain = data.domain_string.split('.')
            if len(data_domain) > 1 and has_match_obj:
                val_obj = obj_dict[data.id].search([
                    (data_domain[-1], '=', line[data.name])], limit=1)
                if not val_obj:
                    error += _(u'\nLine nº%s: %s with value %s \
not found in database') % (line_index + 1, data.name, line[data.name])
                vals[data_domain[0]] = val_obj.id
            # if not has_match_obj:
            else:
                vals[data_domain[0]] = line[data.name]
        return vals, error

    @api.onchange('csv_file')
    def _generate_table(self):
        if not self.csv_file:
            return

        csv_file = base64.b64decode(self.csv_file)
        csvfile = io.StringIO(csv_file.decode('utf-8'))

        csv_lines = csv.DictReader(
            csvfile, delimiter=str(self.csv_delimiter),
            quotechar=self.csv_quote_char)
        preview = '<h3 class="text-center">CSV Lines</h3>'
        preview += '<div>'
        preview += '<table class="table table-striped">'
        preview += '<thead><tr>'
        for item in csv_lines.fieldnames:
            preview += '<th scope="col">%s</th>' % (item)
        preview += '</tr></thead>'
        preview += '<tbody>'

        count = 0
        for line in csv_lines:
            preview += '<tr>'
            for name in csv_lines.fieldnames:
                preview += '<td scope="row">%s</td>' % line[name]
            preview += '</tr>'
            count += 1
            if count == 5:
                break

        preview += '<tr>'
        preview += '</tbody></table><h2 class="text-center">...</h2></div>'
        self.table_html = preview

        lista = []
        for name in csv_lines.fieldnames:
            lista.append((0, 0, {
                'name': name,
            }))

        self.coluna_ids = lista


class DynamicImportLine(models.TransientModel):
    _name = 'dynamic.import.line'

    importer_id = fields.Many2one('dynamic.csv.import')
    name = fields.Char('CSV column name')
    field_odoo = fields.Many2one(
        'ir.model.fields')

    model_id = fields.Many2one(related='importer_id.model_id')
    domain_string = fields.Char(string='Domain')

    identifier = fields.Boolean(string='Use as identifier?')

    @api.onchange('field_odoo')
    def _onchange_field_odoo(self):
        self.domain_string = self.field_odoo.name

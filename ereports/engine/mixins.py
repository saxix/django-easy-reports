import StringIO
from django.template import loader
from django.template.response import TemplateResponse
from django.utils.encoding import smart_str

from ereports.templatetags.ereports import with_widget


class ReportRender(object):
    def __init__(self, report):
        super(ReportRender, self).__init__()
        self.report = report

    def render(self, request, context, **response_kwargs):
        context['total_columns_num'] = len(self.report.headers)
        return super(ReportRender, self).render(request, context, **response_kwargs)


class TemplateRender(object):
    """
    A mixin that can be used to render a template.
    """
    template_name = None
    response_class = TemplateResponse
    content_type = None

    def render(self, request, context, **response_kwargs):
        """
        Returns a response, using the `response_class` for this
        view, with a template rendered with the given context.

        If any keyword arguments are provided, they will be
        passed to the constructor of the response class.
        """
        template = loader.get_template(self.active_template_name)
        # context = self.resolve_context(self.context_data)
        content = template.render(context)
        return content


class XlsRender(object):
    """
    A mixin that can be used to render an xls file.
    """
    content_type = 'application/vnd.ms-excel'

    def _get_styles(self, context):
        from xlwt import easyxf

        FORMATS = {
            'DateColumn': 'DD-MMM-YYYY',
            'DateTimeColumn': 'DD MMD YY hh:mm',
            'TimeColumn': 'hh:mm',
            'IntegerColumn': '#,##',
            'DecimalColumn': '#,##0.00',
            'BooleanColumn': 'general',
            'CurrencyColumn': '"$"#,##0.00);[Red]("$"#,##0.00)',
        }

        styles = {}
        for col in context['report'].display_order():
            col_style = context['report'].get_column_by_name(col)
            styles[col] = easyxf(num_format_str=FORMATS.get(col_style.__class__.__name__, 'general'))

        return styles

    #TODO:
    # handle columns Email, Formulas, etc
    # n = "HYPERLINK"
    # ws.write_merge(1, 1, 1, 10, Formula(n + '("http://www.irs.gov/pub/irs-pdf/f1000.pdf";"f1000.pdf")'), h_style)
    # ws.write(1, 0, xlwt.Formula('A1*B1')) # Should output "10" (A1[5] * A2[2])
    # ws.write(1, 1, xlwt.Formula('SUM(A1,B1)')) # Should output "7" (A1[5] + A2[2])

    def render(self, request, context, **response_kwargs):
        from xlwt import Workbook, XFStyle, easyxf

        w = Workbook(encoding='utf-8')

        ws = w.add_sheet('Report')
        style = XFStyle()

        row = 0
        heading_xf = easyxf('font:height 200; font: bold on; align: wrap on, vert centre, horiz center')
        ws.write(row, 0, '#', style)

        for col, fieldname in enumerate(context['report'].headers, start=1):
            ws.write(row, col, str(fieldname), heading_xf)
            ws.col(col).width = 5000
        ws.row(row).height = 500

        # we have to prepare all the styles before going into the loop
        # to avoid the "More than 4094 XFs (styles)" Error
        styles = self._get_styles(context)
        for rownum, data in enumerate(context['report']):
            ws.write(rownum + 1, 0, rownum + 1)
            for idx, (fieldname, rowvalue) in enumerate(data.items()):
                style = styles[rowvalue.column.name]
                try:
                    ws.write(rownum + 1, idx + 1, with_widget(rowvalue, format='xls'), style)
                except Exception:
                    #logger.warning("TODO refine this exception: %s" % e)
                    ws.write(rownum + 1, idx + 1, smart_str(with_widget(rowvalue)), style)

        f = StringIO.StringIO()
        w.save(f)
        f.seek(0)

        return f.read()

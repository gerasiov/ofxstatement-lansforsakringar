import xlrd
from ofxstatement.parser import StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement, StatementLine


class LansforsakringarPlugin(Plugin):
    """Länsförsäkringar <https://www.lansforsakringar.se>"""

    def get_parser(self, filename):
        return LansforsakringarParser(filename)


class LansforsakringarParser(StatementParser):
    statement = Statement(bank_id='Länsförsäkringar', currency='SEK')

    def __init__(self, filename):
        self.filename = filename
        self.sheet = None

    def parse(self):
        with xlrd.open_workbook(self.filename) as book:
            self.sheet = book.sheet_by_index(0)
            return super().parse()

    def split_records(self):
        rows = self.sheet.get_rows()
        next(rows)  # statement date
        next(rows)  # headers
        return rows

    def parse_record(self, row):
        line = StatementLine()
        line.date = self.parse_datetime(row[0].value)
        line.date_user = self.parse_datetime(row[1].value)
        line.memo = row[2].value
        line.amount = row[3].value
        line.trntype = self.get_type(line)
        return line

    @staticmethod
    def get_type(line):
        if line.amount > 0:
            return 'CREDIT'
        elif line.amount < 0:
            return 'DEBIT'
        else:
            return 'OTHER'

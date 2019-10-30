# _compat_csv.py - python 2 uniocde csv compat from stdlib recipe

import sys

if sys.version_info.major == 2:
    import csv
    import codecs

    try:
        from cStringIO import StringIO
    except ImportError:  # pragma: no cover
        from StringIO import StringIO

    __all__ = ['UnicodeCsvReader', 'UnicodeCsvWriter']


    class UnicodeCsvReader(object):
        """Python 2 CSV reader that iterates over unicode lines."""

        def __init__(self, iterlines, dialect=csv.excel, **kwargs):
            iterbytes = (line.encode('utf-8') for line in iterlines)
            self._reader = csv.reader(iterbytes, dialect=dialect, **kwargs)
            self.dialect = self._reader.dialect

        def __iter__(self):
            return self

        def next(self):
            return [unicode(v, 'utf-8') for v in self._reader.next()]

        @property  # pragma: no cover
        def line_num(self):
            return self._reader.line_num


    class UnicodeCsvWriter(object):

        def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwargs):
            self.queue = StringIO()
            self.writer = csv.writer(self.queue, dialect=dialect, **kwargs)
            self.stream = f
            self.encoder = codecs.getincrementalencoder(encoding)()

        def writerow(self, row):
            self.writer.writerow([s.encode('utf-8') for s in row])
            # Fetch UTF-8 output from the queue ...
            data = self.queue.getvalue()
            data = unicode(data, 'utf-8')
            # ... and reencode it into the target encoding
            data = self.encoder.encode(data)
            # write to the target stream
            self.stream.write(data)
            # empty queue
            self.queue.truncate(0)

        def writerows(self, rows):
            for row in rows:
                self.writerow(row)


else:
    __all__ = []

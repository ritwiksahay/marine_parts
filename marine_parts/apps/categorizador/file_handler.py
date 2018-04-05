import json
import os
from pyexcel import get_records

class FSHandler:
    def leer(self, nomArch):
        pass


class FileHandler(FSHandler):
    # Manejo de excepciones de I/O
    def leer(self, nomArch):
        return json.load(open(nomArch, 'r'))


class ExcelHandler(FSHandler):

    def get_records_from_xls(self,nom_arch):
        return get_records(file_name=nom_arch, library='pyexcel-xls')

    def get_records_from_xlsx(self, nom_arch):
        return get_records(file_name=nom_arch, library='pyexcel-xlsx')

    def leer(self, nomArch):
        ext = os.path.splitext(nomArch)[1].lower()
        if ext == '.xls':
            file = self.get_records_from_xls(nomArch)
        elif ext == '.xlsx':
            file = self.get_records_from_xlsx(nomArch)
        else:
            raise RuntimeError('Only XLS and XLSX file formats are supported.')

        return file

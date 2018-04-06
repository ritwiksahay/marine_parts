from io import BytesIO
import pyexcel as pe


def create_test_file(data, file_type):
    io = BytesIO()
    sheet = pe.Sheet(data)
    io = sheet.save_to_memory(file_type, io)
    io.name = 'test.' + file_type
    return io

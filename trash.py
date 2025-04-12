import os
import tempfile
from xhtml2pdf import pisa
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from xhtml2pdf.files import pisaFileObject

# Получаем путь к шрифту и файлу
current_dir = os.path.dirname(os.path.abspath(__file__))  # Путь к текущей директории
font_path = os.path.join(current_dir, "static", "fonts", "arial.ttf")  # Путь к шрифту

# Путь к пользовательской временной папке
custom_temp_dir = os.path.join(current_dir, "CustomTemp")

# Если папка не существует, создаём её
os.makedirs(custom_temp_dir, exist_ok=True)

# Настроим xhtml2pdf и reportlab на использование этой временной папки
# Устанавливаем пользовательскую временную директорию
tempfile.tempdir = custom_temp_dir

# Регистрация шрифта через reportlab (используем абсолютный путь)
pdfmetrics.registerFont(TTFont('Arial', font_path))

# HTML-шаблон
sourceHtml = f'''
<html>
    <head>
        <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
        <style type="text/css">
            @page {{ size: A4; margin: 1cm; }}
            @font-face {{ font-family: Arial; src: url({font_path.replace(os.sep, "/")}); }}
            p {{ color: red; font-family: Arial; }}
        </style>
    </head>
    <body>
        <p>Русский текст</p>
    </body>
</html>
'''

outputFilename = "test.pdf"

def convertHtmlToPdf(sourceHtml, outputFilename):
    with open(outputFilename, "wb") as resultFile:
        pisaFileObject.getNamedFile = lambda self: self.uri
        pisaStatus = pisa.CreatePDF(sourceHtml, dest=resultFile, encoding='UTF-8')
    return pisaStatus.err

if __name__ == "__main__":
    pisa.showLogging()
    error = convertHtmlToPdf(sourceHtml, outputFilename)
    if error:
        print("Ошибка при создании PDF")
    else:
        print(f"PDF успешно создан: {outputFilename}")

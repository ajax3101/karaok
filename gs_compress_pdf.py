import subprocess
import sys
import os
import shutil

def compress_pdf_with_gs(input_path, output_path, quality='screen'):
    """
    Сжимает PDF с помощью Ghostscript.
    Качество может быть: screen, ebook, printer, prepress.
    """
    if shutil.which("gs") is None:
        print("Ghostscript не найден. Убедитесь, что он установлен и добавлен в PATH.")
        sys.exit(1)

    qualities = {
        'screen': '/screen',     # низкое качество, минимальный размер
        'ebook': '/ebook',       # среднее качество
        'printer': '/printer',   # хорошее качество для печати
        'prepress': '/prepress', # максимальное качество
    }

    if quality not in qualities:
        print("Неверный уровень качества. Используйте: screen, ebook, printer, prepress.")
        sys.exit(1)

    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={qualities[quality]}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]

    try:
        subprocess.run(gs_command, check=True)
        print(f"✅ Сжатый PDF сохранен как: {output_path}")
    except subprocess.CalledProcessError:
        print("❌ Ошибка при сжатии PDF.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python gs_compress_pdf.py input.pdf output.pdf [качество]")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    quality = sys.argv[3] if len(sys.argv) > 3 else 'screen'

    if not os.path.exists(input_pdf):
        print("Файл не найден:", input_pdf)
        sys.exit(1)

    compress_pdf_with_gs(input_pdf, output_pdf, quality)

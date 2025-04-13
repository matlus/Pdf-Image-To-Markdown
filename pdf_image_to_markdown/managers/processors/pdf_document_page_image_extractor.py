import pypdfium2 as pdfium
from PIL import Image
import io

class PdfDocumentPageImageExtractor:
    @staticmethod
    def extract_images(pdf_bytes: bytes) -> list[bytes]:
        pdf_document: pdfium.PdfDocument = pdfium.PdfDocument(io.BytesIO(pdf_bytes))
        page_count: int = len(pdf_document)
        png_images: list[bytes] = []
        for page_number in range(page_count):
            page: pdfium.PdfPage = pdf_document.get_page(page_number)
            bitmap: pdfium.Bitmap = page.render(
                scale=2,
                rotation=0,
            )
            image: Image.Image = bitmap.to_pil()
            output: io.BytesIO = io.BytesIO()
            image.save(output, format="PNG")
            png_bytes: bytes = output.getvalue()
            png_images.append(png_bytes)
            page.close()
            bitmap.close()

        pdf_document.close()
        return png_images
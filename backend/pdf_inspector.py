from pathlib import Path

import pymupdf


def inspect_pdf(pdf_path):
    """
    Inspect a PDF without modifying the original file.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            "PDF file could not be found."
        )

    file_size = pdf_path.stat().st_size

    try:
        document = pymupdf.open(str(pdf_path))

        if document.is_encrypted:
            authenticated = document.authenticate("")

            if not authenticated:
                document.close()

                raise ValueError(
                    "Password-protected PDFs are not supported."
                )

        page_information = []

        total_embedded_images = 0
        total_text_characters = 0

        for page_number, page in enumerate(document, start=1):

            page_images = page.get_images(full=True)

            text = page.get_text("text")

            total_embedded_images += len(page_images)
            total_text_characters += len(text.strip())

            rect = page.rect

            page_information.append({
                "page": page_number,
                "width": round(rect.width, 2),
                "height": round(rect.height, 2),
                "orientation": (
                    "Landscape"
                    if rect.width > rect.height
                    else "Portrait"
                ),
                "embedded_images": len(page_images),
                "text_characters": len(text.strip())
            })

        result = {
            "filename": pdf_path.name,
            "file_size_bytes": file_size,
            "file_size_kb": round(
                file_size / 1024,
                2
            ),
            "file_size_mb": round(
                file_size / (1024 * 1024),
                2
            ),
            "page_count": document.page_count,
            "embedded_image_count": total_embedded_images,
            "text_characters": total_text_characters,
            "has_selectable_text": (
                total_text_characters > 0
            ),
            "pages": page_information
        }

        document.close()

        return result

    except Exception:
        raise
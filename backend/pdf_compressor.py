from pathlib import Path
from io import BytesIO

import os
import tempfile

import pymupdf

from PIL import Image


# Compression candidates, from higher to lower quality.
COMPRESSION_CANDIDATES = [
    (120, 65),
    (110, 60),
    (100, 55),
    (90, 50),
    (80, 45),
    (72, 40),
    (60, 35),
]


def render_page_as_jpeg(page, dpi, quality):
    """
    Render one page in RGB and encode it as an optimized JPEG.
    """

    scale = dpi / 72

    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(scale, scale),
        colorspace=pymupdf.csRGB,
        alpha=False
    )

    image = Image.frombytes(
        "RGB",
        (pixmap.width, pixmap.height),
        pixmap.samples
    )

    image_buffer = BytesIO()

    image.save(
        image_buffer,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True
    )

    return image_buffer.getvalue()


def build_compressed_pdf(
    source_path,
    output_path,
    dpi,
    quality
):
    """
    Build a compressed RGB PDF while preserving page dimensions.
    """

    source_path = Path(source_path)
    output_path = Path(output_path)

    original_document = pymupdf.open(
        str(source_path)
    )

    compressed_document = pymupdf.open()

    try:
        original_metadata = original_document.metadata

        for original_page in original_document:

            original_rect = original_page.rect

            jpeg_bytes = render_page_as_jpeg(
                original_page,
                dpi,
                quality
            )

            new_page = compressed_document.new_page(
                width=original_rect.width,
                height=original_rect.height
            )

            new_page.insert_image(
                new_page.rect,
                stream=jpeg_bytes
            )

        if original_metadata:
            compressed_document.set_metadata(
                original_metadata
            )

        compressed_document.save(
            str(output_path),
            garbage=4,
            deflate=True,
            clean=True
        )

    finally:
        compressed_document.close()
        original_document.close()


def compress_pdf(
    source_path,
    output_path,
    target_kb=500
):
    """
    Try compression candidates until the target is achieved.

    If the target cannot be achieved, retain the smallest
    tested output and report that the target was not met.
    """

    source_path = Path(source_path)
    output_path = Path(output_path)

    if not source_path.exists():
        raise FileNotFoundError(
            "Original PDF does not exist."
        )

    if target_kb <= 0:
        raise ValueError(
            "Target size must be greater than zero."
        )

    target_bytes = int(target_kb * 1024)

    original_size = source_path.stat().st_size

    best_result = None
    best_size = None

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with tempfile.TemporaryDirectory(
        dir=str(output_path.parent)
    ) as temp_directory:

        temp_directory = Path(temp_directory)

        for attempt, (dpi, quality) in enumerate(
            COMPRESSION_CANDIDATES,
            start=1
        ):

            candidate_path = (
                temp_directory
                / f"candidate_{attempt}.pdf"
            )

            build_compressed_pdf(
                source_path=source_path,
                output_path=candidate_path,
                dpi=dpi,
                quality=quality
            )

            candidate_size = candidate_path.stat().st_size

            print(
                f"Attempt {attempt}: "
                f"{dpi} DPI, quality {quality}, "
                f"{candidate_size / 1024:.2f} KB"
            )

            if (
                best_size is None
                or candidate_size < best_size
            ):
                best_size = candidate_size

                # Keep a copy of the best candidate.
                best_result = candidate_path.read_bytes()

            if candidate_size <= target_bytes:
                best_result = candidate_path.read_bytes()
                best_size = candidate_size

                break

    if best_result is None:
        raise RuntimeError(
            "Compression did not produce an output."
        )

    output_path.write_bytes(best_result)

    output_size = output_path.stat().st_size

    reduction_percent = (
        (original_size - output_size)
        / original_size
        * 100
    ) if original_size else 0

    # Verify that the output is a valid PDF with all pages.
    verification_document = pymupdf.open(
        str(output_path)
    )

    try:
        output_pages = verification_document.page_count

        original_document = pymupdf.open(
            str(source_path)
        )

        try:
            original_pages = original_document.page_count

            if output_pages != original_pages:
                raise RuntimeError(
                    "Verification failed: page count changed."
                )

            dimensions_preserved = all(
                abs(
                    original_document[index].rect.width
                    - verification_document[index].rect.width
                ) < 0.1
                and abs(
                    original_document[index].rect.height
                    - verification_document[index].rect.height
                ) < 0.1
                for index in range(original_pages)
            )

        finally:
            original_document.close()

        if not dimensions_preserved:
            raise RuntimeError(
                "Verification failed: page dimensions changed."
            )

    finally:
        verification_document.close()

    return {
        "original_size_bytes": original_size,
        "compressed_size_bytes": output_size,
        "original_size_kb": round(
            original_size / 1024,
            2
        ),
        "compressed_size_kb": round(
            output_size / 1024,
            2
        ),
        "target_kb": target_kb,
        "target_met": output_size <= target_bytes,
        "reduction_percent": round(
            reduction_percent,
            2
        ),
        "page_count": output_pages,
        "dimensions_preserved": dimensions_preserved,
        "output_path": str(output_path)
    }
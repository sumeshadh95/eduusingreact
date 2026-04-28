"""Imagen prediction parsing."""

from services.ai_inline_image_parser import decoded_image


def extract_imagen_prediction(data: dict) -> tuple:
    image = next((image_data(item) for item in data.get("predictions") or [] if image_data(item)[0]), None)
    if not image:
        raise RuntimeError("Imagen returned no image data.")
    encoded, mime_type = image
    return decoded_image(encoded, mime_type)


def image_data(prediction: dict) -> tuple[str, str]:
    image = prediction.get("image", {})
    encoded = prediction.get("bytesBase64Encoded") or image.get("bytesBase64Encoded")
    mime_type = prediction.get("mimeType") or image.get("mimeType")
    return (encoded, mime_type)

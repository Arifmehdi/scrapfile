from PIL import Image
import pytesseract

# Load the image from file
image = Image.open('path/to/your/image.png')

# Perform OCR on the image
text = pytesseract.image_to_string(image)

# Print the extracted text
print(text)
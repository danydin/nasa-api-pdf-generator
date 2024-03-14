import requests, os
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from dotenv import load_dotenv

# for custom path instead of just the default .env
dotenv_path = './secrets.env'
# Load variables from .env file into environment
load_dotenv(dotenv_path)
# Access variables
api_key = os.getenv("apiKey")
print(api_key)

def fetch_nasa_image_and_description(api_key):
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    image_url = data.get("url")
    # print(f"Date: {data.get('date')}")
    date = data.get("date")
    description = data.get("explanation")
    return image_url, description, date


def save_image_from_url(url, filename):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image.save(filename)
    return filename


def create_pdf_with_image_and_text(image_path, text, pdf_filename):
    pdf = FPDF()
    pdf.add_page()

    # Load image to get its size
    with Image.open(image_path) as img:
        img_width, img_height = img.size

    # Calculate width and height in mm (FPDF uses mm)
    mm_per_inch = 25.4
    dpi = 96  # Change according to your image's dpi
    pdf_img_width = img_width / dpi * mm_per_inch
    pdf_img_height = img_height / dpi * mm_per_inch

    # Adjust image dimensions to fit the page
    max_width = pdf.w - 20
    max_height = pdf.h - 30 - 20  # minus header and bottom margin
    scale_factor = min(max_width / pdf_img_width, max_height / pdf_img_height)
    new_width = pdf_img_width * scale_factor
    new_height = pdf_img_height * scale_factor

    # Add image
    pdf.image(image_path, x=10, y=30, w=new_width)

    # Start text below the image
    pdf.set_y(30 + new_height + 10)  # 10 mm buffer below the image

    # Add text
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)

    ## === Text will sometimes be on top of the image ======
    # # Add image
    # pdf.image(image_path, x=10, y=30, w=pdf.w - 20)  # Adjust dimensions as needed

    # # Add text
    # pdf.set_font("Arial", size=12)
    # pdf.ln(140)  # Move below the image; adjust as needed
    # pdf.multi_cell(0, 10, text)
    ## ===  END === Text will sometimes be on top of the image ======

    # Save PDF
    pdf.output(pdf_filename)

    print(f"Image and pdf files created!! {pdf_filename}")


def main():
    NASA_API_KEY = api_key  # Replace with your NASA API key
    image_url, description, date = fetch_nasa_image_and_description(NASA_API_KEY)

    image_path = save_image_from_url(image_url, "nasa_image.jpg")

    # header_text = f"NASA Image of the Day: {date}"

    create_pdf_with_image_and_text(
        image_path, description, "nasa_image_with_description.pdf"
    )


if __name__ == "__main__":
    main()


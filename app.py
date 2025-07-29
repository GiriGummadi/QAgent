import os
import tempfile
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import openai
import docx
import pytesseract
from PIL import Image
import pandas as pd
import cv2
import fitz
from ultralytics import YOLO
from functools import lru_cache
from flask import send_from_directory


app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}
@lru_cache(maxsize=1)
def get_yolo_model():
    return YOLO('yolov8n.pt')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_content_from_pdf(file_path):
    logger.info("Extracting content from PDF: %s", file_path)
    content_sequence = []

    with fitz.open(file_path) as doc:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                logger.debug("Extracted text from PDF page %d: %s", page_num, text[:100])
                content_sequence.append(("text", text.strip()))

            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                img_bytes = base_image["image"]
                temp_image_path = os.path.join(tempfile.gettempdir(), f"temp_image_{page_num}_{img_index}.png")
                with open(temp_image_path, "wb") as img_file:
                    img_file.write(img_bytes)
                logger.debug("Extracted image from PDF page %d, image index %d", page_num, img_index)

                image_text = extract_text_from_image(temp_image_path)
                content_sequence.append(("image_text", image_text))
                components_summary = detect_components(temp_image_path)
                content_sequence.append(("components", components_summary))
    
    return content_sequence

def extract_content_from_docx(file_path):
    logger.info("Extracting content from DOCX: %s", file_path)
    content_sequence = []
    doc = docx.Document(file_path)

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            logger.debug("Extracted text from DOCX: %s", text[:100])
            content_sequence.append(("text", text))
    
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_data = rel.target_part.blob
            temp_image_path = os.path.join(tempfile.gettempdir(), "temp_image.png")
            with open(temp_image_path, "wb") as img_file:
                img_file.write(image_data)
            logger.debug("Extracted image from DOCX")

            image_text = extract_text_from_image(temp_image_path)
            content_sequence.append(("image_text", image_text))
            components_summary = detect_components(temp_image_path)
            content_sequence.append(("components", components_summary))

    return content_sequence

def extract_content_from_image(file_path):
    logger.info("Extracting content from uploaded image: %s", file_path)
    content_sequence = []
    image_text = extract_text_from_image(file_path)
    content_sequence.append(("image_text", image_text))
    components_summary = detect_components(file_path)
    content_sequence.append(("components", components_summary))
    return content_sequence

def extract_text_from_image(file_path):
    logger.debug("Performing OCR on image: %s", file_path)
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    logger.debug("Extracted text from image: %s", text[:100])
    return text

def detect_components(file_path):
    logger.debug("Detecting UI components in image: %s", file_path)
    img = cv2.imread(file_path)

    model = get_yolo_model()
    results = model(img)

    components_summary = ""
    for result in results:
        for detection in result.boxes:
            x1, y1, x2, y2, conf, class_id = detection.xyxy[0]
            label = model.names[int(class_id)]
            components_summary += f"Detected component: {label} at coordinates ({int(x1)}, {int(y1)}, {int(x2)}, {int(y2)})\n"
            logger.debug("Detected component: %s at coordinates (%d, %d, %d, %d)", label, int(x1), int(y1), int(x2), int(y2))

    return components_summary

def generate_test_cases(content_sequence):
    logger.info("Generating test cases using OpenAI API")
    combined_content = ""
    for item_type, item_content in content_sequence:
        if item_type == "text":
            combined_content += f"{item_content}\n\n"
        elif item_type == "image_text":
            combined_content += f"Image Text: {item_content}\n\n"
        elif item_type == "components":
            combined_content += f"UI Components:\n{item_content}\n\n"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a QA test case generation assistant. I will provide you with the content of a Software Requirements Specification (SRS) document, "
                "which may include plain text as well as detected text and components from product design images or screenshots. "
                "Your task is to analyze the content in sequence and generate a comprehensive list of QA test cases."
            )
        },
        {
            "role": "user",
            "content": (
                "Generate test cases without including column headers. I only need the test cases in the following format for Excel. Each test case should include the following fields in a detailed manner:\n\n"
                "- Test Case ID: A unique identifier (e.g.- TC01, TC02)\n"
                "- Test Case Description: A detailed description explaining what the test case is validating.\n"
                "- Preconditions: Specify all preconditions necessary before running the test (e.g., user must be logged in, task must exist, etc.).\n"
                "- Test Steps: Provide all the necessary steps to execute the test case with serial numbers. Each step should be clear and detailed.\n"
                "- Expected Result: A clear description of the expected system behavior or UI changes after the test steps are executed.\n"
                "- Status: Set to 'Not yet executed'.\n"
                "- Comments: Leave this field empty.\n\n"
                "Generate the test cases as a list, where each test case is on a new line and follows the format: Test Case ID| Test Case Description| Preconditions| Test Steps| Expected Result| Status| Comments. Ensure there are no additional bullet points or formatting."
                "Here is the content:\n" + combined_content
            )
        }
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
            max_tokens=3000
        )
        logger.debug("OpenAI API response: %s", response)
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Failed to generate test cases using OpenAI API: %s", str(e))
        return ""

def parse_test_cases(generated_output):
    logger.info("Parsing generated test cases")
    test_cases = []
    lines = generated_output.strip().split("\n")

    for line in lines:
        if line.strip():
            test_case_data = line.split('|')
            if len(test_case_data) >= 5:  
                test_cases.append({
                    'Test Case ID': test_case_data[0].strip(),
                    'Test Case Description': test_case_data[1].strip(),
                    'Preconditions': test_case_data[2].strip(),
                    'Test Steps': test_case_data[3].strip(),
                    'Expected Result': test_case_data[4].strip(),
                    'Status': 'Not yet executed',
                    'Comments': '-'
                })
            else:
                logger.warning("Unexpected format in line: %s", line)

    logger.debug("Parsed test cases: %s", test_cases)
    return test_cases

def write_to_excel(test_cases, filename='output.xlsx'):
    logger.info("Writing test cases to Excel file: %s", filename)
    df = pd.DataFrame(test_cases)

    # Save the file to the same temp directory used in the download route
    temp_dir = tempfile.gettempdir()
    full_path = os.path.join(temp_dir, filename)

    with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Test Cases', index=False)

@app.route('/qa_testcases', methods=['POST'])
def upload_srs_file():
    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist('file')
    if not files or any(f.filename == '' for f in files):
        logger.error("No file selected for uploading")
        return jsonify({"error": "No file selected for uploading"}), 400

    content_sequence = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(tempfile.gettempdir(), filename)
            file.save(file_path)
            logger.info("Processing uploaded file: %s", filename)

            if filename.endswith('.docx'):
                content_sequence.extend(extract_content_from_docx(file_path))
            elif filename.endswith('.pdf'):
                content_sequence.extend(extract_content_from_pdf(file_path))
            elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                content_sequence.extend(extract_content_from_image(file_path))
            else:
                logger.error("Unsupported file type: %s", filename)
                return jsonify({"error": f"Unsupported file type: {filename}"}), 400
        else:
            logger.error("File type not allowed for %s", file.filename)
            return jsonify({"error": f"File type not allowed for {file.filename}"}), 400

    if not content_sequence:
        logger.error("No content extracted from the files")
        return jsonify({"error": "No content extracted from the files"}), 400

    generated_output = generate_test_cases(content_sequence)
    test_cases = parse_test_cases(generated_output)

    if not test_cases:
        logger.error("No test cases generated")
        return jsonify({"error": "No test cases generated"}), 400

    write_to_excel(test_cases)
    logger.info("Test cases generated and saved to Excel file")
    return jsonify({"message": "Test cases generated and saved to Excel file", "output": generated_output}), 200

@app.route('/output.xlsx', methods=['GET'])
def download_excel():
    temp_dir = tempfile.gettempdir()
    return send_from_directory(temp_dir, 'output.xlsx', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)


import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
# cv2 and numpy are optional - imported when needed
import io
from utils.pii_detector import detect_pii
import re
# presidio-analyzer is optional - only used if available
try:
    from presidio_analyzer import AnalyzerEngine
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    print("⚠️ presidio-analyzer not available - using regex-only PII detection")

# winsound is Windows-only, make it optional
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

# Check if Tesseract is installed
TESSERACT_AVAILABLE = False
try:
    pytesseract.get_tesseract_version()
    TESSERACT_AVAILABLE = True
    print("✅ Tesseract OCR is available")
except Exception as e:
    print(f"⚠️ Tesseract OCR not found in PATH: {e}")
    # Try to find tesseract in common Windows locations
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            try:
                # Verify it works
                pytesseract.get_tesseract_version()
                TESSERACT_AVAILABLE = True
                print(f"✅ Found and configured Tesseract at: {path}")
                break
            except:
                continue
    
    if not TESSERACT_AVAILABLE:
        print("❌ Tesseract OCR not found. Please install from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Or run: winget install --id UB-Mannheim.TesseractOCR")

app = Flask(__name__)

# Configure CORS for production
# In production, specify allowed origins instead of '*'
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
CORS(app, origins=cors_origins, supports_credentials=True)


# POPPLER_PATH - Auto-detect Poppler installation
POPPLER_PATH = None
# Try to find Poppler in common locations
poppler_paths = [
    r"C:\Users\Admin\Downloads\Release-25.11.0-0\poppler-25.11.0\Library\bin",
    r"C:\Users\Admin\Downloads\Release-25.11.0-0\poppler-25.11.0\bin",
    r"C:\Users\Admin\Downloads\Release-25.11.0-0\bin",
    r"C:\Program Files\poppler\bin",
    r"C:\poppler\bin",
]
for path in poppler_paths:
    if os.path.exists(path):
        pdftoppm_path = os.path.join(path, "pdftoppm.exe")
        if os.path.exists(pdftoppm_path):
            POPPLER_PATH = path
            print(f"✅ Found Poppler at: {POPPLER_PATH}")
            break

if POPPLER_PATH is None:
    print("⚠️ Poppler not found. PDF processing may not work.")
    print("   Download from: https://github.com/oschwartz10612/poppler-windows/releases/")


REDACTED_FOLDER = "redacted_documents"
os.makedirs(REDACTED_FOLDER, exist_ok=True)


# Initialize AnalyzerEngine (optional - only if presidio is available)
# Using regex-only detection to save memory
analyzer = None
if PRESIDIO_AVAILABLE:
    try:
        analyzer = AnalyzerEngine()
        print("✅ Presidio AnalyzerEngine available")
    except Exception as e:
        print(f"⚠️ Presidio initialization failed: {e}")
        analyzer = None
else:
    print("ℹ️ Using regex-only PII detection (presidio-analyzer not installed)")

def play_alert_sound():
    """Play alert sound if available (Windows only)"""
    if WINSOUND_AVAILABLE:
        try:
            frequency = 1000  
            duration = 500  
            winsound.Beep(frequency, duration)
        except Exception:
            # Silently fail if sound can't be played
            pass
    # On Linux/Unix, we can't play sounds, so just skip  



CONTEXT_REFERENCES = {
    "CREDIT_CARD_NUMBER": [
        "my credit card number is", 
        "here is my credit card", 
        "this is my card number", 
        "use this card for payment",
        "enter my credit card details"
    ],
    "DEBIT_CARD_NUMBER": [
        "my debit card number is", 
        "here is my debit card", 
        "this is my ATM card number", 
        "use this for the transaction"
    ],
    "AADHAAR_NUMBER": [
        "my Aadhaar card number is", 
        "Aadhaar number is", 
        "this is my UIDAI number", 
        "provide my Aadhaar"
    ],
    "PAN_NUMBER": [
        "my PAN number is", 
        "here is my PAN", 
        "this is my tax ID"
    ],
    "PASSPORT_NUMBER": [
        "my passport number is", 
        "passport details are", 
        "this is my travel document number"
    ],
    "DRIVING_LICENSE": [
        "my driving license number is", 
        "license details are", 
        "this is my DL number"
    ],
    "BANK_ACCOUNT_NUMBER": [
        "my bank account number is", 
        "account number is", 
        "deposit it in this account",
        "transfer money to this account"
    ],
    "IFSC_CODE": [
        "the IFSC code is", 
        "use this bank IFSC", 
        "branch IFSC is"
    ],
    "UPI_ID": [
        "send money to this UPI", 
        "my UPI ID is", 
        "pay me at this UPI handle"
    ],
    "PHONE_NUMBER": [
        "my phone number is", 
        "here is my contact number", 
        "call me at this number"
    ],
    "EMAIL_ADDRESS": [
        "my email address is", 
        "send it to my email", 
        "contact me at this email"
    ]
}


PII_CATEGORIES = {
    "AADHAAR_NUMBER": r"\b\d{4}\s\d{4}\s\d{4}\b",
    "PAN_NUMBER": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    "PASSPORT_NUMBER": r"\b[A-Z]{1}[0-9]{7}\b",
    "DRIVING_LICENSE": r"\b[A-Z]{2}\d{2}\s\d{4}\s\d{7}\b",
    "CREDIT_CARD_NUMBER": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "DEBIT_CARD_NUMBER": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "BANK_ACCOUNT_NUMBER": r"\b\d{9,18}\b",
    "IFSC_CODE": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    "UPI_ID": r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b",
    "PHONE_NUMBER": r"\b\d{10}\b",
    "EMAIL_ADDRESS": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
}



def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy.
    """
    try:
        import cv2
        import numpy as np
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return Image.fromarray(thresholded)
    except (ImportError, NameError):
        # If OpenCV or numpy is not available, return image as-is
        return image


def redact_text(text, detected_pii):
    """
    Redact sensitive information in the text.
    """
    for pii_type, values in detected_pii.items():
        for value in values:
            text = text.replace(value, "[REDACTED]")
    return text


def mask_image(image, detected_pii, redaction_level):
    """
    Mask sensitive information in the image based on the selected redaction level.
    """
    from utils.pii_detector import PII_LEVEL_MAPPING

    
    levels_order = ['basic', 'intermediate', 'critical']

    try:
        import cv2
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except ImportError:
        # If OpenCV is not available, return image as-is
        return image

    
    custom_config = r"--oem 3 --psm 6"
    try:
        data = pytesseract.image_to_data(
            image, output_type=pytesseract.Output.DICT, config=custom_config
        )
    except Exception as e:
        print(f"OCR Error in mask_image: {str(e)}")
        # Return original image if OCR fails
        return image
    print(data)
    
    for i in range(len(data["text"])):
        text = data["text"][i].strip()  
        if text:  
            for pii_type, values in detected_pii.items():
                
                if PII_LEVEL_MAPPING.get(pii_type, "basic") in levels_order[: levels_order.index(redaction_level) + 1]:
                    for value in values:
                        
                        if value.strip() in text:
                            
                            x, y, w, h = (
                                data["left"][i],
                                data["top"][i],
                                data["width"][i],
                                data["height"][i],
                            )
                            
                            try:
                                import cv2
                                cv2.rectangle(
                                    image_cv, (x, y), (x + w, y + h), (0, 0, 0), -1
                                )
                            except ImportError:
                                pass

    try:
        import cv2
        import numpy as np
        return Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
    except (ImportError, NameError):
        return image


@app.route("/upload", methods=["POST"])
def upload_document():
    try:
        # Check if Tesseract is available
        if not TESSERACT_AVAILABLE:
            return jsonify({"error": "Tesseract OCR is not installed. Please install Tesseract OCR to process documents."}), 500
        
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        
        redaction_level = request.form.get("redaction_level", "basic").lower()
        levels_order = ["basic", "intermediate", "critical"]
        if redaction_level not in levels_order:
            redaction_level = "basic"  

        
        file_bytes = file.read()

        
        if file.filename.lower().endswith(".pdf"):
            try:
                poppler_kwarg = {"poppler_path": POPPLER_PATH} if POPPLER_PATH else {}
                images = convert_from_bytes(file_bytes, **poppler_kwarg)
                text = ""
                all_detected_pii = {}  
                redacted_images = []

                for image in images:
                    try:
                        processed_image = preprocess_image(image)
                        custom_config = r"--oem 3 --psm 6"
                        try:
                            extracted_text = pytesseract.image_to_string(processed_image, config=custom_config)
                        except Exception as ocr_error:
                            print(f"OCR Error: {str(ocr_error)}")
                            return jsonify({"error": f"OCR processing failed: {str(ocr_error)}. Please ensure Tesseract OCR is properly installed."}), 500
                        text += extracted_text + "\n"

                        print("Extracted Text from Page:", extracted_text)
                        detected_pii = detect_pii(extracted_text)

                        for pii_type, values in detected_pii.items():
                            if pii_type in all_detected_pii:
                                all_detected_pii[pii_type].extend(v for v in values if v not in all_detected_pii[pii_type])
                            else:
                                all_detected_pii[pii_type] = values.copy()
                    except Exception as e:
                        print(f"Error processing PDF page: {str(e)}")
                        continue

                from utils.pii_detector import PII_LEVEL_MAPPING
                filtered_pii = {
                    pii_type: values
                    for pii_type, values in all_detected_pii.items()
                    if levels_order.index(PII_LEVEL_MAPPING.get(pii_type, "basic")) <= levels_order.index(redaction_level)
                }

                for image in images:
                    masked_image = mask_image(image, filtered_pii, redaction_level)  
                    redacted_images.append(masked_image)

                from fpdf import FPDF
                pdf = FPDF()
                for redacted_image in redacted_images:
                    redacted_image_path = os.path.join(REDACTED_FOLDER, "temp.png")
                    redacted_image.save(redacted_image_path)
                    pdf.add_page()
                    pdf.image(redacted_image_path, x=10, y=10, w=190)
                    os.remove(redacted_image_path)  
                redacted_pdf_path = os.path.join(REDACTED_FOLDER, "redacted_document.pdf")
                pdf.output(redacted_pdf_path)
                redacted_file_url = f"/download/{os.path.basename(redacted_pdf_path)}"
            except Exception as e:
                print(f"Error processing PDF: {str(e)}")
                return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500

        else:
            try:
                image = Image.open(io.BytesIO(file_bytes))
                processed_image = preprocess_image(image)
                custom_config = r"--oem 3 --psm 6"
                try:
                    extracted_text = pytesseract.image_to_string(processed_image, config=custom_config)
                except Exception as ocr_error:
                    print(f"OCR Error: {str(ocr_error)}")
                    return jsonify({"error": f"OCR processing failed: {str(ocr_error)}. Please ensure Tesseract OCR is properly installed."}), 500
                text = extracted_text

                detected_pii = detect_pii(extracted_text)

                from utils.pii_detector import PII_LEVEL_MAPPING
                filtered_pii = {
                    pii_type: values
                    for pii_type, values in detected_pii.items()
                    if levels_order.index(PII_LEVEL_MAPPING.get(pii_type, "basic")) <= levels_order.index(redaction_level)
                }

                masked_image = mask_image(image, filtered_pii, redaction_level)  
                redacted_image_path = os.path.join(REDACTED_FOLDER, "redacted_image.png")
                masked_image.save(redacted_image_path)
                redacted_file_url = f"/download/{os.path.basename(redacted_image_path)}"
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                return jsonify({"error": f"Cannot process file: {str(e)}"}), 400

        redacted_text = redact_text(text, filtered_pii)

        return jsonify(
            {
                "text": text,
                "redacted_text": redacted_text,
                "detected_pii": filtered_pii,
                "redacted_file_url": redacted_file_url,  
            }
        )
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(REDACTED_FOLDER, filename, as_attachment=True)

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for deployment"""
    return jsonify({"status": "healthy", "service": "PII Redaction API"}), 200

if __name__ == "__main__":
    # Development mode only
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    
    print(f"Starting Flask server in DEVELOPMENT mode on http://{host}:{port}")
    print("⚠️  For production, use: gunicorn --worker-class sync --threads 4 -w 1 --bind 0.0.0.0:5000 wsgi:app")
    app.run(host=host, port=port, debug=debug)  
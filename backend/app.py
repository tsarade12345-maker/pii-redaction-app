
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
# cv2 is optional - imported when needed
import numpy as np
import io
from utils.pii_detector import detect_pii
import speech_recognition as sr
import re
from presidio_analyzer import AnalyzerEngine
import winsound
from datetime import datetime

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


# Configure SocketIO for production
# In production, logger and engineio_logger should be False
is_production = os.getenv("FLASK_ENV", "production") == "production"
socketio = SocketIO(
    app, 
    cors_allowed_origins=cors_origins, 
    logger=not is_production, 
    engineio_logger=not is_production,
    async_mode='eventlet'
)

# Socket error handling
@socketio.on_error()
def error_handler(e):
    print('SocketIO Error:', str(e))
    socketio.emit('error', {'message': str(e)})

@socketio.on('connect')
def handle_connect():
    print('👤 Client connected')
    socketio.emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('👤 Client disconnected')


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


# Initialize AnalyzerEngine
# Try to use spaCy model if available, otherwise use default
try:
    import spacy
    # Try to load spaCy model
    try:
        nlp = spacy.load("en_core_web_sm")
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        print("✅ Presidio configured with spaCy model")
    except Exception as spacy_error:
        print(f"⚠️ spaCy model not available: {spacy_error}")
        print("Using default AnalyzerEngine (may have limited PII detection)")
        analyzer = AnalyzerEngine()
except ImportError:
    print("⚠️ spaCy not installed, using default AnalyzerEngine")
    analyzer = AnalyzerEngine()

def play_alert_sound():
    frequency = 1000  
    duration = 500  
    winsound.Beep(frequency, duration)  



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


def detect_pii_audio(text):
    detected_pii = []
    
    
    results = analyzer.analyze(text=text, language="en")

    
    for r in results:
        detected_pii.append((r.entity_type, text[r.start:r.end]))

    
    for category, pattern in PII_CATEGORIES.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            detected_pii.append((category, match.group()))

    if detected_pii:
        print("\n⚠️ PII Detected! Sensitive Information Found:")
        for entity, value in detected_pii:
            print(f"🔴 Entity: {entity}, Text: {value}")
        
        play_alert_sound()  
        return True

    return False
    


def detect_context(text):
    for pii_type, phrases in CONTEXT_REFERENCES.items():
        for phrase in phrases:
            if phrase.lower() in text.lower():
                print(f"⚠️ Potential PII Context Detected: {pii_type}")
                play_alert_sound()
                return pii_type  
    return None


def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy.
    """
    try:
        import cv2
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return Image.fromarray(thresholded)
    except ImportError:
        # If OpenCV is not available, return image as-is
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
        return Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
    except ImportError:
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

        socketio.emit("pii_detected", {"detected_pii": filtered_pii})

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

# Global variable to track transcription state
is_transcribing = False

@socketio.on("start_transcription")
def handle_transcription(data):
    global is_transcribing
    
    if is_transcribing:
        print("⚠️ Transcription already in progress")
        socketio.emit('error', {'message': 'Transcription already in progress'})
        return
    
    is_transcribing = True
    
    recognizer = sr.Recognizer()
    silence_counter = 0

    try:
        # Notify client that transcription is starting
        socketio.emit('transcription_status', {'status': 'starting'})
        print("🎤 Starting transcription...")
        
        # Check if microphone is available
        try:
            microphone = sr.Microphone()
            # List available microphones for debugging
            mic_list = sr.Microphone.list_microphone_names()
            print(f"📱 Available microphones: {len(mic_list)}")
            if len(mic_list) == 0:
                raise Exception("No microphones found")
        except Exception as mic_error:
            print(f"❌ Microphone error: {str(mic_error)}")
            socketio.emit('error', {'message': f'Microphone not available: {str(mic_error)}'})
            is_transcribing = False
            return
        
        with microphone as source:
            print("🎤 Listening... Speak now!")
            socketio.emit('transcription_status', {'status': 'listening'})
            
            # Adjust for ambient noise with timeout
            try:
                print("🔊 Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Adjusted for ambient noise")
            except Exception as noise_error:
                print(f"⚠️ Could not adjust for noise: {str(noise_error)}")
                # Continue anyway

            while silence_counter < 6 and is_transcribing:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio)

                    print("📝 Transcription:", text)

                    # Send transcription update to client
                    print(f"📤 Sending transcription_update -> {text}")
                    socketio.emit("transcription_update", {
                        "text": text,
                        "timestamp": str(datetime.now())
                    })

                    # Check for PII in context
                    context_pii = detect_context(text)
                    if context_pii:
                        print(f"📤 Sending pii_alert (context) -> {context_pii}")
                        socketio.emit("pii_alert", {
                            "type": context_pii,
                            "value": text,
                            "source": "context",
                            "timestamp": str(datetime.now())
                        })

                    # Check for PII in content
                    if detect_pii_audio(text):
                        print(f"📤 Sending pii_alert (content) -> PII detected")
                        socketio.emit("pii_alert", {
                            "type": "PII",
                            "value": text,
                            "source": "content",
                            "timestamp": str(datetime.now())
                        })

                    silence_counter = 0

                except sr.WaitTimeoutError:
                    print("⏳ No speech detected, still listening...")
                    socketio.emit('transcription_status', {'status': 'waiting'})
                    silence_counter += 1
                except sr.UnknownValueError:
                    print("❌ Could not understand the audio")
                    socketio.emit('transcription_status', {'status': 'unclear'})
                except sr.RequestError as e:
                    print(f"❌ API unavailable: {str(e)}")
                    socketio.emit('error', {'message': f'Speech recognition service unavailable: {str(e)}'})
                    socketio.emit('transcription_status', {'status': 'error', 'message': str(e)})
                    break
                except Exception as e:
                    print(f"❌ Unexpected error in transcription loop: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    socketio.emit('error', {'message': f'Transcription error: {str(e)}'})
                    # Continue listening
                    continue

        print("🔴 Transcription stopped")
        socketio.emit("transcription_complete", {
            "status": "done",
            "reason": "timeout" if silence_counter >= 6 else "stopped"
        })
    
    except KeyboardInterrupt:
        print("🛑 Transcription interrupted by user")
        socketio.emit('transcription_status', {'status': 'stopped'})
    except Exception as e:
        print(f"❌ Error in transcription: {str(e)}")
        import traceback
        traceback.print_exc()
        socketio.emit('error', {'message': f'Transcription failed: {str(e)}'})
        socketio.emit('transcription_status', {'status': 'error', 'message': str(e)})
    
    finally:
        is_transcribing = False
        print("🔴 Transcription stopped and cleaned up")

@socketio.on("stop_transcription")
def handle_stop_transcription():
    global is_transcribing
    print("🛑 Stop transcription requested")
    is_transcribing = False
    socketio.emit('transcription_status', {'status': 'stopped'})

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
    print("⚠️  For production, use: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 wsgi:app")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)  
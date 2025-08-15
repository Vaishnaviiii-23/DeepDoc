from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from datetime import datetime
from PIL import Image
import pytesseract
import re

app = FastAPI()

# CORS (allow your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://deepdoc.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to your tesseract.exe (update if different)
pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------
# Medical info (descriptions + advice)
# ---------------------------
medical_info = {
    # CBC
    "Hemoglobin": {
        "normal_range": "13.8-17.2 g/dL (men), 12.1-15.1 g/dL (women)",
        "description": "Hemoglobin carries oxygen in your blood.",
        "low_meaning": "Low hemoglobin can cause fatigue and anemia.",
        "high_meaning": "High hemoglobin might indicate dehydration or other conditions.",
        "advice": "Eat iron-rich foods (spinach, lentils, red meat) and consult a doctor if low."
    },
    "Hematocrit": {
        "normal_range": "40.7%-50.3% (men), 36.1%-44.3% (women)",
        "description": "Hematocrit measures the proportion of red blood cells in the blood.",
        "low_meaning": "Low hematocrit can indicate anemia.",
        "high_meaning": "High hematocrit may indicate dehydration or polycythemia.",
        "advice": "Stay hydrated and consult a doctor for abnormal results."
    },
    "RBC": {
        "normal_range": "4.7-6.1 million/mcL (men), 4.2-5.4 million/mcL (women)",
        "description": "Red blood cells carry oxygen from lungs to body tissues.",
        "low_meaning": "Low RBC may cause anemia and fatigue.",
        "high_meaning": "High RBC may indicate dehydration or lung/heart disease.",
        "advice": "Follow medical advice; maintain nutrition and hydration."
    },
    "WBC": {
        "normal_range": "4,000-11,000 cells/µL",
        "description": "White blood cells fight infection.",
        "low_meaning": "Low WBC may increase infection risk.",
        "high_meaning": "High WBC may indicate infection or inflammation.",
        "advice": "Consult a doctor if abnormal."
    },
    "Neutrophils": {
        "normal_range": "40-60 % (of WBC)",
        "description": "Neutrophils fight bacterial infections.",
        "low_meaning": "Low neutrophils increase infection risk.",
        "high_meaning": "High neutrophils often indicate bacterial infection.",
        "advice": "Seek medical advice if abnormal."
    },
    "Lymphocytes": {
        "normal_range": "20-40 % (of WBC)",
        "description": "Lymphocytes fight viral infections.",
        "low_meaning": "Low lymphocytes may weaken immune defense.",
        "high_meaning": "High lymphocytes may indicate viral infection or chronic conditions.",
        "advice": "Monitor symptoms and consult a doctor if needed."
    },
    "Monocytes": {
        "normal_range": "2-8 % (of WBC)",
        "description": "Monocytes clean up debris and help fight infections.",
        "low_meaning": "Low monocytes may indicate bone marrow problems.",
        "high_meaning": "High monocytes may indicate infection or inflammation.",
        "advice": "Consult healthcare provider."
    },
    "Eosinophils": {
        "normal_range": "1-4 % (of WBC)",
        "description": "Eosinophils are involved in allergies and parasitic infections.",
        "low_meaning": "Low eosinophils usually not a concern.",
        "high_meaning": "High eosinophils can indicate allergies or parasites.",
        "advice": "Discuss allergy testing or treatment with your doctor."
    },
    "Basophils": {
        "normal_range": "0.5-1 % (of WBC)",
        "description": "Basophils play a role in allergic responses.",
        "low_meaning": "Low basophils usually not clinically important.",
        "high_meaning": "High basophils may suggest allergies or inflammation.",
        "advice": "Talk to your healthcare provider for context."
    },
    "Platelets": {
        "normal_range": "150,000-450,000 /µL",
        "description": "Platelets help with blood clotting.",
        "low_meaning": "Low platelets increase bleeding/bruising risk.",
        "high_meaning": "High platelets may raise clotting risk.",
        "advice": "Avoid injury and consult a doctor if abnormal."
    },
    "MPV": {
        "normal_range": "7.5-11.5 fL",
        "description": "Mean platelet volume indicates average platelet size.",
        "low_meaning": "Low MPV may indicate production problems.",
        "high_meaning": "High MPV may indicate increased platelet production.",
        "advice": "Discuss with your clinician."
    },

    # Lipid profile
    "Cholesterol (Total)": {
        "normal_range": "<200 mg/dL",
        "description": "Total cholesterol is all cholesterol types combined.",
        "low_meaning": "Low total cholesterol not usually concerning.",
        "high_meaning": "High total cholesterol increases heart disease risk.",
        "advice": "Reduce saturated fat and exercise."
    },
    "HDL Cholesterol": {
        "normal_range": ">=40 mg/dL (men), >=50 mg/dL (women)",
        "description": "HDL is 'good' cholesterol.",
        "low_meaning": "Low HDL increases cardiovascular risk.",
        "high_meaning": "High HDL is usually protective.",
        "advice": "Exercise and healthy fat intake help increase HDL."
    },
    "LDL Cholesterol": {
        "normal_range": "<100 mg/dL (optimal)",
        "description": "LDL is 'bad' cholesterol that can clog arteries.",
        "low_meaning": "Low LDL typically fine.",
        "high_meaning": "High LDL increases heart disease risk.",
        "advice": "Lifestyle changes and medication if recommended."
    },
    "Triglycerides": {
        "normal_range": "<150 mg/dL",
        "description": "Triglycerides are fats stored for energy.",
        "low_meaning": "Low triglycerides usually not a concern.",
        "high_meaning": "High triglycerides increase heart disease risk.",
        "advice": "Reduce sugar, alcohol; maintain healthy weight."
    },

    # Kidney function
    "Blood Urea Nitrogen (BUN)": {
        "normal_range": "7-20 mg/dL",
        "description": "BUN is a kidney function marker.",
        "low_meaning": "Low BUN may indicate liver issues.",
        "high_meaning": "High BUN may suggest kidney dysfunction or dehydration.",
        "advice": "Stay hydrated and consult doctor if high."
    },
    "Creatinine": {
        "normal_range": "0.6-1.3 mg/dL",
        "description": "Creatinine reflects kidney performance.",
        "low_meaning": "Low creatinine usually not concerning.",
        "high_meaning": "High creatinine suggests reduced kidney function.",
        "advice": "Consult a doctor for elevated values."
    },
    "Uric Acid": {
        "normal_range": "3.5-7.2 mg/dL",
        "description": "Uric acid is a waste product from purine metabolism.",
        "low_meaning": "Low values usually not concerning.",
        "high_meaning": "High levels may cause gout.",
        "advice": "Limit purine-rich foods if high; consult physician."
    },

    # Electrolytes
    "Sodium": {
        "normal_range": "135-145 mmol/L",
        "description": "Sodium helps control water balance and nerve function.",
        "low_meaning": "Low sodium (hyponatremia) can cause confusion and seizures.",
        "high_meaning": "High sodium suggests dehydration.",
        "advice": "Correct fluid balance under medical advice."
    },
    "Potassium": {
        "normal_range": "3.5-5.0 mmol/L",
        "description": "Potassium is vital for heart and muscle function.",
        "low_meaning": "Low potassium can cause weakness or irregular heartbeat.",
        "high_meaning": "High potassium can endanger heart rhythm.",
        "advice": "Follow medical guidance; dietary changes may help."
    },
    "Chloride": {
        "normal_range": "96-106 mmol/L",
        "description": "Chloride helps maintain acid-base balance.",
        "low_meaning": "Low chloride can occur with vomiting or dehydration.",
        "high_meaning": "High chloride may indicate kidney/adrenal issues.",
        "advice": "Consult your clinician for abnormal values."
    },

    # Liver function
    "ALT (SGPT)": {
        "normal_range": "7-56 U/L",
        "description": "ALT is a liver enzyme; elevated levels may indicate liver damage.",
        "low_meaning": "Low levels are normal.",
        "high_meaning": "High ALT suggests liver injury or inflammation.",
        "advice": "Avoid alcohol and discuss further evaluation."
    },
    "AST (SGOT)": {
        "normal_range": "10-40 U/L",
        "description": "AST is a liver/muscle enzyme.",
        "low_meaning": "Low levels are normal.",
        "high_meaning": "High AST can indicate liver or muscle damage.",
        "advice": "Follow up with healthcare provider."
    },
    "Alkaline Phosphatase (ALP)": {
        "normal_range": "44-147 IU/L",
        "description": "ALP relates to liver and bone health.",
        "low_meaning": "Low ALP usually not concerning.",
        "high_meaning": "High ALP may indicate liver/bone disease.",
        "advice": "Consult a doctor when elevated."
    },
    "Bilirubin (Total)": {
        "normal_range": "0.1-1.2 mg/dL",
        "description": "Bilirubin is produced by breakdown of red blood cells.",
        "low_meaning": "Low bilirubin is normal.",
        "high_meaning": "High bilirubin causes jaundice; check liver function.",
        "advice": "Seek medical evaluation if elevated."
    },
    "Albumin": {
        "normal_range": "3.4-5.4 g/dL",
        "description": "Albumin is a protein made by the liver.",
        "low_meaning": "Low albumin can indicate liver disease or malnutrition.",
        "high_meaning": "High albumin is uncommon (dehydration).",
        "advice": "Assess nutrition and liver health with provider."
    },

    # Thyroid
    "TSH": {
        "normal_range": "0.4-4.0 mIU/L",
        "description": "TSH controls thyroid function.",
        "low_meaning": "Low TSH may indicate hyperthyroidism.",
        "high_meaning": "High TSH may indicate hypothyroidism.",
        "advice": "See an endocrinologist for abnormal results."
    },
    "T3": {
        "normal_range": "80-200 ng/dL",
        "description": "T3 is an active thyroid hormone.",
        "low_meaning": "Low T3 may indicate hypothyroid state.",
        "high_meaning": "High T3 may indicate hyperthyroidism.",
        "advice": "Discuss with your doctor."
    },
    "T4": {
        "normal_range": "4.6-12.0 µg/dL",
        "description": "T4 is the main thyroid hormone.",
        "low_meaning": "Low T4 may indicate hypothyroidism.",
        "high_meaning": "High T4 may indicate hyperthyroidism.",
        "advice": "Follow up for thyroid testing if abnormal."
    },

    # Diabetes markers
    "Glucose (Fasting)": {
        "normal_range": "70-100 mg/dL",
        "description": "Fasting blood glucose measures sugar after not eating.",
        "low_meaning": "Low glucose can cause dizziness and confusion.",
        "high_meaning": "High fasting glucose may indicate diabetes/prediabetes.",
        "advice": "Monitor diet, exercise, and follow medical advice."
    },
    "Glucose (PP)": {
        "normal_range": "<140 mg/dL (2 hrs after meal)",
        "description": "Postprandial glucose measures blood sugar after eating.",
        "low_meaning": "Low values rarely concerning.",
        "high_meaning": "High PP glucose may indicate impaired glucose handling.",
        "advice": "Consult provider about diabetes testing."
    },
    "HbA1c": {
        "normal_range": "<5.7 %",
        "description": "HbA1c indicates average blood sugar over ~3 months.",
        "low_meaning": "Low HbA1c is uncommon and usually fine.",
        "high_meaning": "High HbA1c indicates prediabetes or diabetes.",
        "advice": "Lifestyle changes and medical care advised when high."
    },
    # Vitamins & minerals (examples)
    "Vitamin D": {
        "normal_range": {"default": "20-50 ng/mL"},
        "description": "Vitamin D aids bone health and immunity.",
        "low_meaning": "Low Vitamin D can cause bone weakness.",
        "high_meaning": "High Vitamin D is rare but can be toxic.",
        "advice": "Supplementation if deficient as guided by clinician."
    },
    "Vitamin B12": {
        "normal_range": {"default": "200-900 pg/mL"},
        "description": "B12 is important for nerve health and blood formation.",
        "low_meaning": "Low B12 can cause anemia and neuropathy.",
        "high_meaning": "High B12 usually not harmful but investigate causes.",
        "advice": "Supplement if deficient."
    },

    # Inflammatory markers
    "CRP": {
        "normal_range": {"default": "<3 mg/L"},
        "description": "C-reactive protein, a marker of inflammation.",
        "low_meaning": "Low CRP is normal.",
        "high_meaning": "High CRP indicates inflammation or infection.",
        "advice": "Investigate source of inflammation."
    },
    "ESR": {
        "normal_range": {"male": "0-15 mm/hr", "female": "0-20 mm/hr", "default": "0-20 mm/hr"},
        "description": "Erythrocyte sedimentation rate, an inflammation marker.",
        "low_meaning": "Low ESR is not a concern.",
        "high_meaning": "High ESR suggests inflammation.",
        "advice": "Correlate clinically."
    },

    # Hormones (examples)
    "PSA": {
        "normal_range": {"male": "<4.0 ng/mL"},
        "description": "Prostate-specific antigen (male).",
        "low_meaning": "Low PSA is normal.",
        "high_meaning": "High PSA may suggest prostate disease.",
        "advice": "Urology referral if elevated."
    }
    # You can add more parameters here as needed.
}

# ---------------------------
# Aliases and thresholds (gender-specific where applicable)
# ---------------------------
param_aliases = {
    "Hemoglobin": ["hemoglobin", "hb", "hgb"],
    "Hematocrit": ["hematocrit", "hct"],
    "RBC": ["rbc", "red blood cell", "red blood cells"],
    "WBC": ["wbc", "white blood cell", "total wbc", "total wbc count"],
    "Neutrophils": ["neutrophil", "neutrophils"],
    "Lymphocytes": ["lymphocyte", "lymphocytes"],
    "Monocytes": ["monocyte", "monocytes"],
    "Eosinophils": ["eosinophil", "eosinophils"],
    "Basophils": ["basophil", "basophils"],
    "Platelets": ["platelet", "platelets", "plt"],
    "MPV": ["mpv", "mean platelet volume"],
    "Cholesterol (Total)": ["cholesterol", "total cholesterol"],
    "HDL Cholesterol": ["hdl", "hdl cholesterol"],
    "LDL Cholesterol": ["ldl", "ldl cholesterol"],
    "Triglycerides": ["triglyceride", "triglycerides", "tg"],
    "Blood Urea Nitrogen (BUN)": ["bun", "blood urea nitrogen", "urea"],
    "Creatinine": ["creatinine", "scr"],
    "Uric Acid": ["uric acid", "uricacid"],
    "Sodium": ["sodium", "na"],
    "Potassium": ["potassium", "k"],
    "Chloride": ["chloride", "cl"],
    "ALT (SGPT)": ["alt", "sgpt"],
    "AST (SGOT)": ["ast", "sgot"],
    "Alkaline Phosphatase (ALP)": ["alp", "alkaline phosphatase"],
    "Bilirubin (Total)": ["bilirubin", "bilirubin total", "total bilirubin"],
    "Albumin": ["albumin"],
    "TSH": ["tsh"],
    "T3": ["t3"],
    "T4": ["t4"],
    "Glucose (Fasting)": ["glucose fasting", "fasting glucose", "glucose (fasting)", "fbs", "fasting blood sugar"],
    "Glucose (PP)": ["pp glucose", "postprandial glucose", "ppbs", "pp"],
    "HbA1c": ["hba1c", "a1c"],
    # Vitamins / others
    "Vitamin D": ["vitamin d", "vit d", "25-ohd"],
    "Vitamin B12": ["vitamin b12", "b12"],
    "CRP": ["crp"],
    "ESR": ["esr"],
    "PSA": ["psa"]
}

# thresholds: support gender-specific ranges where applicable
# format: { param: {"male": (low,high), "female": (low,high), "default":(low,high)} }
param_thresholds = {
    "Hemoglobin": {"male": (13.8, 17.2), "female": (12.1, 15.1), "default": (12.1, 17.2)},
    "Hematocrit": {"male": (40.7, 50.3), "female": (36.1, 44.3), "default": (36.1, 50.3)},
    "RBC": {"male": (4.7, 6.1), "female": (4.2, 5.4), "default": (4.2, 6.1)},
    "WBC": {"default": (4000, 11000)},
    "Neutrophils": {"default": (40, 60)},
    "Lymphocytes": {"default": (20, 40)},
    "Monocytes": {"default": (2, 8)},
    "Eosinophils": {"default": (1, 4)},
    "Basophils": {"default": (0.5, 1)},
    "Platelets": {"default": (150000, 450000)},
    "MPV": {"default": (7.5, 11.5)},
    "Cholesterol (Total)": {"default": (0, 200)},
    "HDL Cholesterol": {"male": (40, 9999), "female": (50, 9999), "default": (40, 9999)},
    "LDL Cholesterol": {"default": (0, 100)},
    "Triglycerides": {"default": (0, 150)},
    "Blood Urea Nitrogen (BUN)": {"default": (7, 20)},
    "Creatinine": {"default": (0.6, 1.3)},
    "Uric Acid": {"default": (3.5, 7.2)},
    "Sodium": {"default": (135, 145)},
    "Potassium": {"default": (3.5, 5.0)},
    "Chloride": {"default": (96, 106)},
    "ALT (SGPT)": {"default": (7, 56)},
    "AST (SGOT)": {"default": (10, 40)},
    "Alkaline Phosphatase (ALP)": {"default": (44, 147)},
    "Bilirubin (Total)": {"default": (0.1, 1.2)},
    "Albumin": {"default": (3.4, 5.4)},
    "TSH": {"default": (0.4, 4.0)},
    "T3": {"default": (80, 200)},    # units vary — these are approximate
    "T4": {"default": (4.6, 12.0)},
    "Glucose (Fasting)": {"default": (70, 100)},
    "Glucose (PP)": {"default": (0, 140)},
    "HbA1c": {"default": (0, 5.7)},
     "Vitamin D": {"default": (20, 50)},
    "Vitamin B12": {"default": (200, 900)},
    "CRP": {"default": (0, 3)},
    "ESR": {"male": (0, 15), "female": (0, 20), "default": (0, 20)},
    "PSA": {"male": (0, 4.0)}
}

# ---------------------------
# Helper functions
# ---------------------------

def extract_number(s):
    """Try to extract a numeric value from a string robustly."""
    if s is None:
        return None
    # normalize unicode punctuation that OCR often produces
    s = s.replace("‘", "").replace("’", "").replace("“", "").replace("”", "")
    # replace weird characters often seen in OCR for minus or decimal
    s = s.replace("—", "-").replace("−", "-")
    # remove commas used as thousand separators or trailing commas
    s = re.sub(r"(?<=\d)[,](?=\d{3}\b)", "", s)
    # remove stray non-number characters except . and - and %
    # but keep percent sign to detect percent values
    # first handle percentage values (e.g., "12 %")
    perc = re.search(r"(-?\d+\.?\d*)\s*%", s)
    if perc:
        try:
            return float(perc.group(1))
        except:
            return None
    m = re.search(r"(-?\d+\.?\d*)", s)
    if m:
        try:
            return float(m.group(1))
        except:
            return None
    return None

def detect_gender_from_text(text):
    """Try to detect gender from OCR text. Returns ('male'|'female'|'unknown', source)."""
    if not text:
        return "unknown", "none"
    lowered = text.lower()
    # common patterns
    if re.search(r"\bsex[:\s]*male\b", lowered) or re.search(r"\bsex[:\s]*m\b", lowered) or re.search(r"\bmale\b", lowered):
        return "male", "ocr"
    if re.search(r"\bsex[:\s]*female\b", lowered) or re.search(r"\bsex[:\s]*f\b", lowered) or re.search(r"\bfemale\b", lowered):
        return "female", "ocr"
    # try shorter patterns like "M 25Y" or "F 30 Y"
    if re.search(r"\bM\b[\s,]\d{1,2}\b", text):
        return "male", "ocr"
    if re.search(r"\bF\b[\s,]\d{1,2}\b", text):
        return "female", "ocr"
    return "unknown", "ocr"

def get_threshold_for_param(param, gender="unknown"):
    """Return (low, high) based on param_thresholds and gender."""
    info = param_thresholds.get(param)
    if not info:
        return None, None
    # prefer gender-specific
    if gender and gender.lower() in info:
        return info[gender.lower()]
    if "default" in info:
        return info["default"]
    # fallback to any numeric tuple
    for v in info.values():
        if isinstance(v, (tuple, list)) and len(v) == 2:
            return tuple(v)
    return None, None

# ---------------------------
# Parser
# ---------------------------

def parse_medical_report(text, gender="unknown"):
    """
    Robust parser that:
    - normalizes text into lines,
    - for each parameter alias, finds line with alias and searches that line and next 3 lines for numeric value,
    - fallback: windowed search near alias in the whole text.
    """
    results = {}
    if not text:
        return results

    # normalize newlines and split into non-empty lines
    norm = text.replace("\r", "\n")
    raw_lines = [ln.strip() for ln in norm.splitlines() if ln.strip() != ""]
    lower_lines = [ln.lower() for ln in raw_lines]

    # helper to attempt add param if number found
    def try_add(param_key, value):
        if value is None:
            return False
        low, high = get_threshold_for_param(param_key, gender)
        if low is not None and high is not None:
            if value < low:
                meaning = medical_info[param_key].get("low_meaning", "Below normal range.")
            elif value > high:
                meaning = medical_info[param_key].get("high_meaning", "Above normal range.")
            else:
                meaning = "Within normal range."
        else:
            meaning = "Value found."

        results[param_key] = {
            "value": value,
            "normal_range": medical_info[param_key].get("normal_range", ""),
            "description": medical_info[param_key].get("description", ""),
            "meaning": meaning,
            "advice": medical_info[param_key].get("advice", "")
        }
        return True

    # 1) Line-based scanning
    for param_key, aliases in param_aliases.items():
        found_flag = False
        for i, ln in enumerate(lower_lines):
            for alias in aliases:
                if alias in ln:
                    # search current line and up to next 3 lines for a number
                    for j in range(i, min(i + 4, len(raw_lines))):
                        candidate = raw_lines[j]
                        num = extract_number(candidate)
                        if num is not None:
                            if try_add(param_key, num):
                                found_flag = True
                                break
                    if found_flag:
                        break
            if found_flag:
                break

    # 2) Fallback: windowed search across entire text (handles unusual layouts)
    for param_key, aliases in param_aliases.items():
        if param_key in results:
            continue  # already found
        for alias in aliases:
            # search alias and up to 60 chars following for a number
            m = re.search(rf"{re.escape(alias)}[\s\S]{{0,80}}?([-\d.,%]+)", text, re.IGNORECASE)
            if m:
                candidate = m.group(1)
                num = extract_number(candidate)
                if num is not None:
                    try_add(param_key, num)
                    break

    return results

# ---------------------------
# Upload endpoint
# ---------------------------

@app.post("/upload")
async def upload_report(file: UploadFile = File(...), user_gender: str = Form(None)):
    """
    Accepts uploaded image (PDF not handled here) and optional form field 'user_gender' (male/female).
    Returns extracted raw_text, detected gender, parsed_results.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # save file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # OCR
    try:
        img = Image.open(filepath)
        # convert if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        extracted_text = pytesseract.image_to_string(img)
    except Exception as e:
        extracted_text = ""
        print("OCR error:", e)

    # detect gender via OCR unless user provided an explicit gender
    detected_gender = "unknown"
    gender_source = "none"
    if user_gender and user_gender.lower() in ("male", "female"):
        detected_gender = user_gender.lower()
        gender_source = "user"
    else:
        detected_gender, gender_source = detect_gender_from_text(extracted_text)

    # parse values using gender-aware thresholds
    parsed_results = parse_medical_report(extracted_text, gender=detected_gender)

    # optional summary
    issues = []
    for p, info in parsed_results.items():
        if info.get("meaning") and info["meaning"] != "Within normal range.":
            issues.append(f"{p}: {info['meaning']}")

    summary = "All parameters are within normal ranges." if not issues else "Issues: " + "; ".join(issues)

    return {
        "filename": file.filename,
        "detected_gender": detected_gender,
        "gender_source": gender_source,
        "raw_text": extracted_text,
        "parsed_results": parsed_results,
        "summary": summary
    }

#  🩺👩‍⚕️DeepDoc — Real-Time Medical Report Translator & Visualizer

An AI-powered web app that lets users upload medical reports and instantly receive simplified explanations, parameter highlights, and personalized health advice.
---

##  Repository Overview
```DeepDoc/
│
├── backend/
│ ├── main.py # FastAPI backend logic
│ ├── requirements.txt # Python dependencies
│ └── uploads/ # Stores uploaded reports
│
├── frontend/
│ ├── public/ # Static frontend assets
│ ├── src/ # React source code
│ ├── package.json # Frontend dependencies
│ └── .gitignore # Ignored frontend files
│
├── .gitignore # Root ignore rules
└── README.md # Project overview
```

---

##  Features

- **Image/Text Upload**: Upload report images for analysis.
- **OCR Extraction**: Converts images to extract medical text.
- **Parameter Analysis**: Identifies key medical metrics (e.g., hemoglobin, WBC) and categorizes them.
- **Human-Friendly Recommendations**: Displays easy-to-understand meanings and medical advice directly on the page.
- **Gender-Aware Interpretation**: Uses gender input to adjust normal range evaluations.
- **Frontend Grouping**: Organized UI by category — CBC, Liver, Kidney, and more.

---

## Tech Stack

**Frontend**  
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![React Icons](https://img.shields.io/badge/React%20Icons-61DAFB?style=for-the-badge&logo=react&logoColor=white)

**Backend**  
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-4B8BBE?style=for-the-badge&logo=python&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-92C021?style=for-the-badge&logo=python&logoColor=white)
![pytesseract](https://img.shields.io/badge/Tesseract-5D92CB?style=for-the-badge&logo=google&logoColor=white)
![Regex](https://img.shields.io/badge/Regex-FF9800?style=for-the-badge&logo=regex&logoColor=white)


---

##  Setup & Run Locally

### Clone Repository
```bash
git clone https://github.com/Vaishnaviiii-23/DeepDoc.git
cd DeepDoc
cd backend
python -m venv env
. env/Scripts/activate 
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend will run at: http://localhost:8000

### Frontend
```bash
cd frontend
npm install
npm start
```
Open in browser: http://localhost:3000

## 📸 Screenshots

### Frontend  
![Upload Report](./screenshots/upload_report.png)

### Uploaded report and extracted parameters  
![Extracted Parameters](./screenshots/extracted_parameters.png)

### OCR Results
![OCR Result](./screenshots/ocr_result.png)

## Contribution Guidelines

Feel free to contribute! Please:

Fork the repo

Create a new branch (feature/…)

Make changes and push your branch

Open a Pull Request

## 🧑‍💻 Author
Vaishnavi P Poojari
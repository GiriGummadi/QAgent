# 🤖 QAgent – Automated QA Test Case Generation Tool

QAgent is an intelligent web-based tool that automates the generation of **QA test cases** from documents and screenshots using the power of AI. Just upload a Software Requirements Specification (SRS) file or a UI image, click a button, and get a well-formatted Excel file with detailed test cases — ready for your QA team to use.

---

## 🚀 What It Does

QAgent reads through:

- 📄 **SRS documents** (.docx or .pdf)
- 🖼️ **UI screenshots or mockups** (.png, .jpg, .jpeg)

Then:

1. Extracts **text** and **UI components** using OCR and YOLO (object detection).
2. Feeds the structured information to the **OpenAI GPT-4 model**.
3. Automatically **generates detailed test cases** in Excel-ready format (Test Case ID, Description, Preconditions, Steps, Expected Result, Status, Comments).

---

## 🧠 Why It Matters

In real-world QA workflows, teams spend **hours manually writing test cases** from functional specs and design screens. This process is:

- Time-consuming
- Prone to human error
- Tedious and repetitive

QAgent changes the game by using AI to **automate this process**, saving QA engineers hours of manual work while improving coverage and consistency.

---

## 🛠️ Technologies Used

### 🔹 Frontend (React + Next.js)

- **React 19** with **Next.js 15**
- **Tailwind CSS 4** for fast, responsive UI design
- **Radix UI + Lucide Icons** for beautiful accessible components
- **React Hot Toast** for notifications

### 🔹 Backend (Python + Flask)

- **Flask** API with file handling and response routing
- **OpenAI GPT-4 API** to generate test cases from structured content
- **Pytesseract** for OCR text extraction from images
- **YOLOv8** (via Ultralytics) to detect UI components like buttons, inputs, dropdowns
- **fitz (PyMuPDF)** for reading PDF files
- **docx (python-docx)** for reading Word documents
- **Pandas** to format and write Excel output
- **OpenCV** and **PIL** for image processing
- **ExcelWriter (xlsxwriter)** to save the final output

---

## 📁 Project Structure

QAgent/
│
├── app.py # Flask backend
├── requirements.txt # Backend dependencies
├── frontend/ # Next.js + React frontend
│ ├── pages/
│ ├── components/
│ └── ...
├── Input files/ # Uploaded SRS or image files
├── Generated Output/ # Auto-generated Excel files
├── Input images/ # Temporary image extractions
└── .gitignore

---

## ⚙️ How It Works (Under the Hood)

1. **User uploads file from frontend**

   - Frontend sends a `POST` request to `/qa_testcases` with the uploaded files.

2. **Backend processes files**

   - PDF/DOCX → text via `fitz` and `docx`
   - Images → text via `pytesseract`, components via YOLO

3. **Combined data is fed to GPT-4**

   - Prompted with a structured instruction to generate test cases

4. **Test cases parsed and saved**

   - Output saved as `output.xlsx` in temp directory

5. **User downloads result**
   - Frontend provides direct link to `/output.xlsx` to download test cases

---

## 🌍 Real-World Use Cases

| Scenario               | Impact                                                                    |
| ---------------------- | ------------------------------------------------------------------------- |
| 🔧 **Manual QA Teams** | Automatically generate dozens of test cases from lengthy requirement docs |
| 🧪 **Agile Startups**  | Speed up sprint testing with quick turnaround                             |
| 🧩 **UI/UX Designers** | Validate designs by generating test expectations from screenshots         |
| 🏢 **Enterprises**     | Standardize test case formatting and reduce errors                        |

---

## 📌 Skills Demonstrated

- End-to-end **Full Stack Development**
- AI Integration with **OpenAI GPT-4 API**
- Working with unstructured documents and **OCR**
- Object detection using **YOLOv8**
- **Excel automation** using Python
- Clean and responsive **UI/UX** using modern React stack
- Git, GitHub project management

---

## 📜 License

This project is open-source and free to use under the MIT License.

---

## 🙌 Author

Built by **Giri Ratna Sai Gummadi**  
🔗 [LinkedIn](https://www.linkedin.com/in/girigummadi) | 🌐 [GitHub](https://github.com/GiriGummadi)

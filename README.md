# TODOS
## Important
- [ ] make display of information look nice and add feature to instantly copy paste the output
- [ ] optimize dictionary with medicine names and often used words
- [ ] change regex depending on how the structure is like

## Nice to have
- [ ] add option that recognizes when there is an error with missing numbers or medicine and show that to pharmacist with red tint or so, so they definitely manually check that again
- [ ] fine tune OCR with examples (you can artificially create them as well, after you at least got the basic structure down and then train the model with that)


# 💊 Smart Intake: AI-Powered Prescription Reader

**Smart Intake** is a lightweight, AI-powered desktop tool that lets pharmacists drag-and-drop prescription images or PDFs and automatically extracts structured medication information using state-of-the-art handwriting OCR (via Microsoft's TrOCR model).

Built with **Electron + Python + Hugging Face Transformers**, it supports both **modern typed prescriptions** and **scanned handwritten faxes**.

---

## 🚀 Features

- 📄 Drag & drop or upload **PDFs / JPEGs / PNGs**
- 🧠 AI-powered OCR using `microsoft/trocr-base-handwritten`
- 🧾 Extracts:
  - Patient name
  - Date of birth
  - Prescriber (doctor) name
  - Medication names, dosages, and sig (instructions)
- 📤 Outputs a structured JSON-like preview and lets you **"Send to RxConnect"**
- 💻 Works **offline**, runs locally (no data leaves your machine)

---

## 🖥 Demo

https://user-images.githubusercontent.com/yourvideo.gif  
📽 _Coming soon: full walkthrough GIF_

---

## 📦 Tech Stack

| Layer        | Tech Used                                     |
|-------------|------------------------------------------------|
| Frontend    | [Electron](https://www.electronjs.org/), HTML, JS |
| Backend     | Python 3.12+, Hugging Face Transformers        |
| OCR Model   | `microsoft/trocr-base-handwritten`             |
| File I/O     | `pdf2image`, `Pillow`, `fs`                   |

---

## 🛠 Installation

### ✅ Prerequisites

- Node.js (v18+ recommended)
- Python 3.10 or 3.12 (✅ PyTorch supported version)
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) installed & added to `PATH` (for PDF rasterizing)

---

### 🔧 Clone + Setup

```bash
git clone https://github.com/yourusername/smart-intake.git
cd smart-intake

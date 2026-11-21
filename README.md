# AI-Based Viva Question Generator

A Streamlit mini project that reads a project report PDF using PyPDF2 and asks an LLM to create 15 likely viva questions with short answers: 5 Easy, 5 Medium and 5 Hard.

## Features
- Upload a PDF project report.
- Extract selectable text from all PDF pages using PyPDF2.
- Preview extracted text.
- Generate exactly 15 questions and answers using Google Gemini's API.
- Display questions in Easy, Medium and Hard tabs.
- Download the generated Q&A as a text file.

## Requirements
- Python 3.9+
- Gemini API key (from [Google AI Studio](https://aistudio.google.com/app/apikey))

## Setup (Windows)
1. Extract the ZIP file.
2. Open Command Prompt in the project folder.
3. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file in this folder and add your API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
   You can also paste the key into the sidebar when the app is running.
   Keep `.env` private. Never upload it to GitHub.
6. Run:
   ```bash
   streamlit run app.py
   ```

## How to use
1. Open the local Streamlit URL shown in the terminal.
2. Upload a text-based project report PDF.
3. Click **Generate 15 Viva Questions**.
4. Review the Easy, Medium and Hard questions and download the answers.

## Important limitations
- Scanned/image-only PDFs may not contain selectable text. OCR must be added for those files.
- AI-generated questions are likely practice questions, not guaranteed exam questions.
- The app uses the first 60,000 extracted characters for the prompt.
- API usage may incur charges depending on the account and model pricing.

## Project workflow
PDF upload -> PyPDF2 text extraction -> prompt construction -> Gemini LLM -> 15 Q&A -> Streamlit display/export.

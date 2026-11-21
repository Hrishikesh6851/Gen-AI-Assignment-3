import os
import json
import re
import streamlit as st
from PyPDF2 import PdfReader
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Viva Question Generator", page_icon="🎓", layout="wide")

st.title("🎓 AI-Based Viva Question Generator")
st.write("Upload your project report and generate 15 likely viva questions with short answers.")

with st.sidebar:
    st.header("Configuration")
    key_input = st.text_input("Gemini API key", type="password",
                              help="Leave blank to use GEMINI_API_KEY from your .env file.")
api_key = key_input.strip() or os.getenv("GEMINI_API_KEY")

uploaded_file = st.file_uploader("Upload your project report (PDF)", type=["pdf"])

def extract_pdf_text(pdf_file):
    """Extract text from every page of the uploaded PDF."""
    reader = PdfReader(pdf_file)
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(f"[Page {page_number}]\n{page_text}")
    return "\n\n".join(pages), len(reader.pages)

def generate_prompt(report_text):
    return f"""
You are an expert project viva examiner and student mentor.
Read the project report below and generate exactly 15 likely viva questions
with short, clear, student-friendly answers.

Requirements:
- Generate exactly 5 EASY, 5 MEDIUM, and 5 HARD questions.
- Questions must be based on the uploaded report. Do not invent project features,
  results, tools, datasets, or facts that are not supported by the report.
- Easy: project introduction, problem statement, objectives, basic definitions.
- Medium: methodology, architecture, modules, tools, implementation and workflow.
- Hard: design choices, limitations, testing, challenges, evaluation and future scope.
- Answers should normally be 2–4 sentences and suitable for speaking in a viva.
- If the report does not contain enough information for a question, do not ask it.
- Return ONLY valid JSON, with this exact structure:
{{
  "project_title": "title found in report or 'Not specified'",
  "easy": [{{"question": "...", "answer": "..."}}],
  "medium": [{{"question": "...", "answer": "..."}}],
  "hard": [{{"question": "...", "answer": "..."}}]
}}

PROJECT REPORT TEXT:
{report_text}
"""

def call_llm(report_text, key):
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=generate_prompt(report_text),
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=8192,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction="You generate accurate viva preparation material from project reports."
        )
    )
    raw = (response.text or "").strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
    return json.loads(raw)

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")
    try:
        report_text, page_count = extract_pdf_text(uploaded_file)
        st.info(f"PDF pages: {page_count} | Extracted characters: {len(report_text):,}")

        if not report_text.strip():
            st.error("No selectable text was found. This may be a scanned PDF. Please upload a text-based PDF or OCR it first.")
        else:
            with st.expander("Preview extracted report text"):
                st.text(report_text[:5000] + ("\n\n[Preview shortened]" if len(report_text) > 5000 else ""))

            if st.button("Generate 15 Viva Questions", type="primary", disabled=not bool(api_key)):
                if not api_key:
                    st.error("Enter your Gemini API key in the sidebar or add GEMINI_API_KEY to your .env file.")
                else:
                    # Keep the prompt within a practical context size.
                    text_for_model = report_text[:60000]
                    if len(report_text) > 60000:
                        st.warning("The report is long. The first 60,000 characters will be used.")
                    with st.spinner("Reading the report and preparing questions..."):
                        try:
                            result = call_llm(text_for_model, api_key)
                            expected = {"easy": 5, "medium": 5, "hard": 5}
                            valid = all(isinstance(result.get(level), list) and len(result[level]) == count
                                        for level, count in expected.items())
                            if not valid:
                                st.error("The AI did not return exactly 5 questions in each level. Please try again.")
                            else:
                                st.session_state["viva_result"] = result
                        except Exception as exc:
                            st.error(f"Could not generate questions: {exc}")

    except Exception as exc:
        st.error(f"Could not read this PDF: {exc}")

result = st.session_state.get("viva_result")
if result:
    st.divider()
    st.subheader(f"Questions for: {result.get('project_title', 'Your Project')}")
    tabs = st.tabs(["Easy (5)", "Medium (5)", "Hard (5)"])
    for tab, level in zip(tabs, ["easy", "medium", "hard"]):
        with tab:
            for index, item in enumerate(result[level], start=1):
                with st.expander(f"Q{index}. {item['question']}", expanded=(index == 1)):
                    st.markdown(f"**Answer:** {item['answer']}")

    export_text = []
    export_text.append(f"Viva Questions: {result.get('project_title', 'Project')}\n")
    for level in ["easy", "medium", "hard"]:
        export_text.append(f"\n{level.upper()} QUESTIONS\n")
        for index, item in enumerate(result[level], start=1):
            export_text.append(f"{index}. {item['question']}\nAnswer: {item['answer']}\n")
    st.download_button("⬇️ Download Questions and Answers (.txt)",
                       data="\n".join(export_text),
                       file_name="viva_questions.txt",
                       mime="text/plain")
else:
    st.caption("Your generated questions will appear here after you upload a PDF and click Generate.")

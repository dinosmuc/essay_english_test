import streamlit as st
import openai
import yaml
import random
import PyPDF2
import chardet
import io
from docx import Document

# Function to handle PDF files
def read_pdf(uploaded_file):
    # Read the file as a byte stream
    file_stream = io.BytesIO(uploaded_file.read())
    pdf_reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to handle Word documents
def read_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

# Function to read text files with uncertain encoding
def read_text(file):
    raw_data = file.read()
    encoding = chardet.detect(raw_data)['encoding']
    return raw_data.decode(encoding)

# Theme and Layout 
st.set_page_config(page_title="English Proficiency Assessment", layout="wide")
st.markdown("""
      <style>
      .big-font {
          font-size:20px !important;
          font-weight: bold;
      }
      </style>
      """, unsafe_allow_html=True)

# Load API credentials
try:
    with open('chatgpt_api_credentials.yml', 'r') as file:
        api_creds = yaml.safe_load(file)
except:
    api_creds = {}

# Sidebar for API Key Input
with st.sidebar:
    st.markdown("## Settings")
    openai_api_key = api_creds.get("openai_key", "")
    if openai_api_key:
        st.success("OpenAI API key is provided.")
    else:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        openai.api_key = openai_api_key

# Main Application
st.title("Assess Your English Skills Through Essay Writing")

# Essay Topic Selection
col1, col2 = st.columns([3, 1])
st.markdown("### 📘 Generate an Essay Topic")
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.session_state.get('topic', '')
    if st.button("Generate a Topic"):
        if openai_api_key:
            with st.spinner('Generating a topic...'):
                prompt = """Generate a simple essay topic suitable for assessing English proficiency.
                            Use this template: <"essay topic">
                         """
                response = openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=prompt,
                    temperature=1,
                    max_tokens=50
                )
                topic = response.choices[0].text.strip()
                st.session_state['topic'] = topic
        else:
            st.error("Please provide the OpenAI API key to generate a topic.")
    st.markdown(f"<p class='big-font'>{topic}</p>", unsafe_allow_html=True)

# File Uploader
# File Uploader
uploaded_file = st.file_uploader("", type=("txt", "pdf", "docx"), key="file_uploader")

if uploaded_file:
    grade_button = st.button('Process Essay')
    if grade_button and openai_api_key:
        with st.spinner('Processing your essay...'):
            # Check the file type
            if uploaded_file.type == "text/plain":
                essay = read_text(uploaded_file)
            elif uploaded_file.type == "application/pdf":
                essay = read_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                essay = read_docx(uploaded_file)
            else:
                st.error("Unsupported file type")
                st.stop()


            # Grading Prompt
            essay_proficiency_analysis = f"""
                Here is an essay:

                {essay}

                Based on this essay, assess the English language proficiency level. 
                Please use the CEFR scale to rate the essay. 
                Consider factors such as grammar, vocabulary, sentence structure, and overall fluency.
                
                Output only rate in form:
                <CEFR scale rate> 
            """

            # Analysis Prompt
            essay_analysis = f"""
                Here is an essay:

                {essay}

                First, assess if the essay is relevant to the topic: '{topic}'. 
                If it is off-topic, state 'The essay is not on the assigned topic.'

                If the essay is on-topic, proceed to analyze the English proficiency demonstrated. 
                Focus on grammar, vocabulary, syntax, and overall language effectiveness. 
                Identify the key strengths and any areas for improvement. 
                Summarize your findings, offering a concise overview of the essay's English proficiency.
            """

            # Connect to ChatGPT
            

            # Generate Responses
            response1 = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=essay_proficiency_analysis,
                temperature=0,
                max_tokens=10
            )
            response2 = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=essay_analysis,
                temperature=0.7,
                max_tokens=256
            )

            # Display Grade and Analysis
            grade = response1.choices[0].text.strip()
            analysis = response2.choices[0].text.strip()

            # Using columns for a side-by-side layout
            col1, col2 = st.columns(2)

            # Displaying the Grade
            st.markdown("### 📊 English Level")
            st.markdown(f"<div style='font-size: 24px; color: green; font-weight: bold;'>{grade}</div>", unsafe_allow_html=True)

            # Displaying the Analysis
            st.markdown("### 📝 Essay Analysis")
            st.markdown(f"<div style='font-size: 18px; color: blue;'>{analysis}</div>", unsafe_allow_html=True)

            st.success("Essay processed!")

            # Question to Teacher
   

st.markdown("---")
st.markdown("Developed by Dino Smuc")

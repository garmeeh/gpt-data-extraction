from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from pytesseract import image_to_string
from PIL import Image
from io import BytesIO
import pypdfium2 as pdfium
import streamlit as st
import multiprocessing
from tempfile import NamedTemporaryFile
import pandas as pd
import json

load_dotenv()

# 1. Convert PDF file into images via pypdfium2
def convert_pdf_to_images(file_path, scale=300/72):

    pdf_file = pdfium.PdfDocument(file_path)

    page_indices = [i for i in range(len(pdf_file))]

    renderer = pdf_file.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=page_indices,
        scale=scale,
    )

    final_images = []

    for i, image in zip(page_indices, renderer):

        image_byte_array = BytesIO()
        image.save(image_byte_array, format='jpeg', optimize=True)
        image_byte_array = image_byte_array.getvalue()
        final_images.append(dict({i: image_byte_array}))

    return final_images

# 2. Extract text from images via pytesseract
def extract_text_from_img(list_dict_final_images):
    image_list = [list(data.values())[0] for data in list_dict_final_images]
    image_content = []

    # pylint: disable=unused-variable
    for _, image_bytes in enumerate(image_list):

        image = Image.open(BytesIO(image_bytes))
        raw_text = str(image_to_string(image))
        image_content.append(raw_text)

    return "\n".join(image_content)


def extract_content_from_url(url: str):
    images_list = convert_pdf_to_images(url)
    text_with_pytesseract = extract_text_from_img(images_list)

    return text_with_pytesseract


# 3. Extract structured info from text via LLM
def extract_structured_data(content: str, data_points):
    llm = ChatOpenAI(temperature=0, model="gpt-4-0613")
    template = """
    You are an expert real estate lawyer and you have been asked to extract the following data points from a real estate purchase agreement:

    {content}

    Above is the content; please try to extract all data points from the content above 
    and export in a JSON array format:
    {data_points}

    Now please extract details from the content  and export in a JSON array format, 
    return ONLY the JSON array:
    """

    prompt = PromptTemplate(
        input_variables=["content", "data_points"],
        template=template,
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    results = chain.run(content=content, data_points=data_points)
    return results

# 4. Streamlit app
def main():
    default_data_points = """{
        "address": "address of the property being sold",
        "purchase_price": "purchase price amount in the form of $X",
        "deposit": "deposit amount in the form of $X",
        "depost_timing": "if any special considerations for deposit timing",
        "due_diligence_period": "length of the due diligence period",
        "closing_date": "defined closing date in the form of YYYY-MM-DD",
        "conditions_precedent": "conditions precedent for closing",
        "casualty_condemnation_provisions": "Summarize the casualty/condemnation provisions",
        "representations_and_warranties": "In detail, list the types of representations and warranties made",
        "disclaimers: "Is there any mention of it being a sale with a disclaimer of warranties. List them if present",
        "closing_costs": "State how closing costs are allocated",
        "remedies": "Summarize the remedies for buyer/seller default",
        "broker": "Identify the broker and commission payable",
        "notice_requirements": "Note the notice requirements",
        "post_closing": "Summarize any details for post-closing requirements",
        "notes: "Make a note of any other important details that may be relevant that have not been captured above"
    }"""

    st.set_page_config(page_title="Doc extraction", page_icon=":bird:")

    st.header("POC: Document Extraction")

    data_points = st.text_area(
        "Data points", value=default_data_points, height=170)

    uploaded_files = st.file_uploader(
        "upload PDFs", accept_multiple_files=True)

    if uploaded_files is not None and data_points is not None:
        results = []
        for file in uploaded_files:
            with NamedTemporaryFile(dir='.', suffix='.csv') as f:
                f.write(file.getbuffer())
                content = extract_content_from_url(f.name)
                data = extract_structured_data(content, data_points)
                json_data = json.loads(data)
                if isinstance(json_data, list):
                    results.extend(json_data)  
                else:
                    results.append(json_data) 

        if len(results) > 0:
            try:
                df = pd.DataFrame(results)
                st.subheader("Results")
                st.data_editor(df)
            except Exception as e:
                st.error(
                    f"An error occurred while creating the DataFrame: {e}")
                st.write(results) 


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()

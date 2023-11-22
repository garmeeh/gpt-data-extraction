# Data Extraction

The core of this code is a fork of [repo](https://github.com/JayZeeDesign/gpt-data-extraction), Jason runs through it in detail in this [YouTube Video](https://youtu.be/v_cfORExneQ?si=6xJGEX40jUbkqySy). Check out the video to get up to speed on the code.

To run this code you will need to install the requirements and then spin up the Streamlit app.

Install the requirements:

```
pip install -r requirements.txt
```

Run the Streamlit app:

```
streamlit run app.py
```

NOTE:

- You will need an OpenAI API key to run this code. Rename the `.env.example` to `.env` and add your key
- You will `tesseract` installed on your machine to run the OCR. If you are on a Mac you can install it with `brew install tesseract`.

Possible Errors:

I hit an error version `5.3.3` on a Apple Silicone Mac. Not sure if it was the M1 chip or the version of tesseract. It runs ok on a Intel Mac running version 5.2.2 of tesseract.

from dotenv import load_dotenv

load_dotenv()  # Load all the environment variables

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import pandas as pd




genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Pro Vision API And get response



def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, image[0], prompt])
    return response.text


# Function to set up image data

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

    
    

# Load car data from CSV
@st.cache
def load_car_data():
    car_data = pd.read_csv("car_data.csv")
    return car_data

#initialize our streamlit app
st.set_page_config(page_title="Car Inspector")

st.header("Car Inspector")

input_prompt = """
You are a car inspector tasked with assessing damage to a {selected_car_brand} {selected_car_model} {chassis_number} {plate_chars}-{plate_numbers} . 
Please examine the image of the car and identify the damaged parts. 
Provide an estimate for the cost to repair each damaged part.
And total cost also, all amounts must be in riyals. 
List the damaged parts and their estimated repair costs in the following format:

1. Part 1 - Cost to repair
2. Part 2 - Cost to repair
----
----

"""

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Load car data
car_data = load_car_data()

# Dropdown for car brand
car_brand = st.selectbox("Select Car Brand", car_data["Brand"].unique())

# Dropdown for car model based on selected brand
car_models = car_data[car_data["Brand"] == car_brand]["Model"].unique()
car_model = st.selectbox("Select Car Model", car_models)

# Dropdown for car color
car_colors = car_data[(car_data["Brand"] == car_brand) & (car_data["Model"] == car_model)]["Color"].unique()
car_color = st.selectbox("Select Car Color", car_colors)

# Input box for chassis number
chassis_number = st.text_input("Chassis Number", max_chars=17)

# Input boxes for number plate characters and numbers on a single line with placeholders
col1, col2 = st.columns(2)
with col1:
    plate_chars = st.text_input("Number Plate ", max_chars=3,placeholder="Please enter the character portion",type="default")
with col2:
    plate_numbers = st.text_input("", max_chars=4,placeholder="Please enter the number portion")

image = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

c1,c2 = st.columns([1,1])

with c1:
    submit = st.button("Predict")
    
with c2:
    next_button_disabled = not submit
    # next_button_clicked = st.markdown('<a href="pages/workshop_list.py" target="_blank" style="padding: 10px 20px; color: blue; text-decoration: none; border-radius: 5px;">Next</a>', unsafe_allow_html=True)
    


# If submit button is clicked and all fields are filled
if submit and uploaded_file is not None and chassis_number != "" and plate_chars != "" and plate_chars.isalpha() and plate_numbers != "":
    selected_car_brand = car_brand
    selected_car_model = car_model
    selected_car_color = car_color
    selected_car_data = car_data[(car_data["Brand"] == selected_car_brand) & 
                                 (car_data["Model"] == selected_car_model) & 
                                 (car_data["Color"] == selected_car_color)]
    
    engine_price = selected_car_data["Engine"].iloc[0]
    bumper_price = selected_car_data["Bumper"].iloc[0]
    tire_price = selected_car_data["Tire"].iloc[0]
    
    prompt_with_values = input_prompt.format(selected_car_brand=selected_car_brand, 
                                             selected_car_model=selected_car_model,
                                             selected_car_color=selected_car_color,
                                             engine_price=engine_price,
                                             bumper_price=bumper_price,
                                             tire_price=tire_price,
                                             chassis_number=chassis_number,
                                             plate_chars=plate_chars,
                                             plate_numbers=plate_numbers)
    
    image_data = input_image_setup(uploaded_file)
    response = get_gemini_response(prompt_with_values, image_data, input_prompt)
    st.subheader("The Response is")
    st.write(response)
elif submit:
    st.error("Please make sure you have selected an image and filled in all the required fields.")
    if not plate_chars.isalpha():
        st.error("Please enter alphabets instead for the character portion.")

# if next_button_clicked:
#     st.experimental_set_query_params(page="pages/workshop_list")        
         

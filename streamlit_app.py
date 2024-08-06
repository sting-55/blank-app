import streamlit as st

st.title("Q&A App")
st.write(
    "Upload an image of a P3 or P4 question."
)

import base64
import requests

with st.form(key='my_form'):
  # OpenAI API Key
  api_key = st.text_input('Enter your API key here:')
  # Streamlit app
  uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])
  submit_button = st.form_submit_button('Submit')


# Paths to your files
#image_path = 'image.png'
topics_file_path = 'topics.txt'
prompts_file_path = 'prompts.txt'


# Function to read topics from a file
def read_topics(file_path):
    with open(file_path, "r") as file:
        topics = [line.strip() for line in file.readlines()]
    return topics

# Function to read prompts from a file
def read_prompts(file_path):
    with open(file_path, "r") as file:
        prompts = [line.strip() for line in file.readlines()]
    return prompts

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')



if submit_button and uploaded_file is not None:
    # Display the uploaded image
    #image_show = Image.open(uploaded_file)
    st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)
    
  # Encode the image

    base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')


  # Read topics and prompts
    topics = read_topics(topics_file_path)
    prompts = read_prompts(prompts_file_path)


    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    classification_prompt = f"Classify the question in this image into one or more of the following topics: {', '.join(topics)}. Only reply with the topic names."

    payload = {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": classification_prompt
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    import json

    # Convert the response to JSON
    response_json = response.json()

    # Accessing the content from the choices
    if 'choices' in response_json and len(response_json['choices']) > 0:
        content = response_json['choices'][0]['message']['content']
        print(content)
    else:
        print("No choices found in the response or the response is empty.")


    # Function to find the best matching chapter based on the input chapter name

    prompt_for_matching = f"Given the following chapter names in {content}, find the relevant prompts section in {prompts}."


    payload_prompt = {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": prompt_for_matching
            }
          ]
        }
      ],
      "max_tokens": 3000
    }

    response_prompt_matching = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload_prompt)

    #print(response_prompt_matching)

    payload_answer = {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": f"answer the questions in the image based on the study notes in {response_prompt_matching}. Answer like a 10 year old elementary student. Link the answer back to the question.Read the question carefully. If it asks for one difference, or one characteristic, etc. keep your answer to describe just one point. Provide clear reasons based on the key concepts"
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 3000
    }

    response_answer = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload_answer)

    #print(response_answer.json())

    # Convert the response to JSON
    response_json_answer = response_answer.json()

    # Accessing the content from the choices
    if 'choices' in response_json_answer and len(response_json_answer['choices']) > 0:
        content = response_json_answer['choices'][0]['message']['content']
        #print(content)
    else:
        print("No choices found in the response or the response is empty.")

    st.write(content)


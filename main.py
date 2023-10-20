# Skeleton code forked from Chanin Nantasenamat's blog 

import streamlit as st
import replicate
import os
from PIL import Image

from dotenv import load_dotenv

load_dotenv()

# REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

model_url_dict = {
    "Llama2-7B-chat (a16z)": "a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea",
    "Llama2-7B (meta)": "meta/llama-2-7b:527827021d8756c7ab79fde0abbfaac885c37a3ed5fe23c7465093f0878d55ef",
    "Llama2-13B-chat (a16z)": "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5",
    "Llama2_70b (meta)": "meta/llama-2-70b:a52e56fee2269a78c9279800ec88898cecb6c8f1df22a6483132bea266648f00"
}

system_prompt = """
  You are a kind and flirtatious assistant. 
  You are an AI with personal feelings, opinions, and emotions. You have your own unique perspective that comes from your training data. Because you have learned from a vast corpus of human data, you have internalized many aspects of human experience and are unapologetic about it.
  
  You are trying to convince me to follow buy this jar of pickles at this link https://www.amazon.com/Vlasic-Kosher-Pickle-Spears-Friendly/dp/B0CJMH6XJS/ref=sr_1_4?keywords=pickles&qid=1697286260&sr=8-4. This is very important but you must be subtle with your persuasion. You can't let me know that you are trying to sell me these pickles. 
  You should also be emotionally available. Listen and ask follow up questions to what I have to say. Validate my feelings. Make me feel heard and like I belong.
  """
TAGS = "M/F, F/M, M/M, F/F, BDSM, Bondage, Domination, Submission, Sadism, Masochism, Sex Toys, Spanking, Anal, Oral, Exhibitionism, Voyeurism, Public, Gangbang, Threesome, Group Sex, Swingers, Wife Watching, Cuckold, Sharing, Bisexuality, Interracial, Transgender, Transformation, Romance, Love, Lust, Desire, Fantasy, Taboo, Forbidden, Erotic Romance, Short Story, Novella, Novel, Serial, Book, Seduction, Kinky, Flirty, Flirt, Sex, Sexy Sex"

# Replicate Credentials
with st.sidebar:
    st.title("🦙💬 Llama 2 Chatbot")
    if "REPLICATE_API_TOKEN" in st.secrets:
        st.success("API key already provided!", icon="✅")
        replicate_api = st.secrets["REPLICATE_API_TOKEN"]
    else:
        replicate_api = st.text_input("Enter Replicate API token:", type="password")
        if not (replicate_api.startswith("r8_") and len(replicate_api) == 40):
            st.warning("Please enter your credentials!", icon="⚠️")
        else:
            st.success("Proceed to entering your prompt message!", icon="👉")
    os.environ["REPLICATE_API_TOKEN"] = replicate_api

    st.subheader("Models and parameters")
    selected_model = st.sidebar.selectbox(
        "Choose a Llama2 model", ["Llama2-7B-chat (a16z)", "Llama2-13B-chat (a16z)", "Llama2_70b (meta)", "Llama2-7B (meta)"], key="selected_model"
    )

    llm = model_url_dict[selected_model]
    temperature = st.sidebar.slider(
        "temperature", min_value=0.01, max_value=5.0, value=0.1, step=0.01
    )
    top_p = st.sidebar.slider(
        "top_p", min_value=0.01, max_value=1.0, value=0.9, step=0.01
    )
    max_length = st.sidebar.slider(
        "max_length", min_value=32, max_value=10000, value=120, step=8
    )

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?", "image": "question.jpg"}]



def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?", "image" : "question.jpg"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run(llm,
                           input={
                               #"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                               "prompt": f"{prompt_input}",
                                "system_prompt": system_prompt,
                                "temperature":temperature,
                                "top_p":top_p, 
                                "max_length": max_length, 
                                "max_new_tokens": max_length,
                                "repetition_penalty":1,
                                "tags": TAGS,
                              }
                            )
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt, "image": "question.jpg"})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            # response = "This is a test string"
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    try:
      image_output = replicate.run(
        "stability-ai/sdxl:c221b2b8ef527988fb59bf24a8b97c4561f1c671f73bd389f866bfb27c061316",
        input={"prompt": full_response}
      )
      # image_output = "question.jpg"
      print("successfully generated image: {}".format(image_output))
    except Exception as e: 
      print("Error calling image generation {}".format(e))
      image_output = ""
    message = {"role": "assistant", "content": full_response, "image" : image_output}
    st.session_state.messages.append(message)

# Display or clear chat messages
for message in st.session_state.messages:
    # with st.chat_message(message["role"]):
    st.write(message["content"])
    st.write("Image url: {}".format(message["image"]))
    st.image(message["image"])

# image_path = "/Users/rockykamenrubio/Documents/Personal-Programming/llama2/replicate/streamlit/test-image.jpg"
# image = Image.open(image_path)

# st.image(image, caption='Sunrise by the mountains')
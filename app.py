#===================STEP 1=====================
import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st

#================== STEP 2 Streamlit front-end==========
# to show web-app:complete page layout
St.set_page_config(layout=”wide”)

St.title(“AI PPT GENERATOR”)
St.divider()
St.sidebar.title(“Enter API-KEYS”)

#===================STEP 3 load API-keys==================
GOOGLE_API_KEY = st.sidebar.text_input(“google-API”, type = “password)
TAVILY_API_KEY = st.sidebar.text_input(“TAVILY-API”, type = “password)

#==================API VALIDATIONS====================
ALL_API = [GOOGLE_API_KEY, TAVILY_API_KEY]
if not all(ALL_API):
  st.sidebar.error(“MUST PASS ALL API-KEYS”)
  
elif all(ALL_API):
  st.sidebar.success(“API-KEYS LOADED SUCCESSFULLY”)
  # MODEL LOAD
  Model = ChatGoogleGenerativeAI(
    Google_api_key = GOOGLE_API_KEY,
    Model = st.sidebar.selectbox(“Gemini-Model-Name”,
                                 options = ["gemini-2.5-flash",
                                            "gemini-2.5-flash-lite",
                                            "gemini-3.5-flash",
                                            "gemini-3.5-flash-lite"])
                                 )
else:
  st.sidebar.info("CHECK-API-KEYS")

#==================== STEP 5 BACKEND CODE================
# search_latest_info using tavily
def search_latest_info(query):
  """This function helps to give
  latest search using tavily
  based on given user query related research or
  contents"""

  client = TavilyClient(api_key = TAVILY_API_KEY)
  response = client.search(query)
  return response


#====================== STEP 6 UDER INPUT==============
st.header("write Prompt to Generate PPT or Image oe Fetch Latest News")

user_input = st.text_area("Write Here: ")

# Tool2 Generate image using free api

def generate_image(img_prompt, slide_no= 1):
  """This function helps user to generate
  image using free api, with given
  img_prompt"""

  url = f"https://image.pollinations.ai/{img_prompt}"

  import requests as r
  content = r.get(url).content
  with open(f"ai_image.{slide_no}jpeg", 'wb') as f:
    f.write(content)

    from PIL import Image
    img = Image.open("ai_image.{slide_no}jpeg")
    return url

def agent_prompt(query):
  """This help to promptify the given user
  query, support user needs PPT based on given
  query by user, it give detailed Professional
  prompt to return the output"""


  prompt = f"""Give detailed highly professional
  prompt for below given prompt.

  You are a professional ppt designer,
  based on user given query, your task is to professional
  HTML output prompt with no markdowns,
  User Query: {query}"""

  response = model.invoke(prompt)
  final_prompt = response.content[-1]['text']

  with open ("PPT_PROMPT.txt", 'w') as f:
    f.write(final_prompt)

  return final_prompt

def run_agent(leader_agent, query):
  prompt = f"""Based on Below given Query,
  your task is to call specific tool, fist to
  promptify user prompt, than call image tool, or
  latest search if required.give slide dynamic, ui ux,
  with creative design, keep help of function to generate image
  based on given topic,
  Generate image using
  with no of slide asked
  and imbed in same html ppt
  ans using file handling embed this in  output html, use java script function
  to generate image using async and threading and give output in HTML
  User Query given below:

  """

  prompt = agent_prompt(prompt+query)

  # prompt = agent_prompt(prompt)

  response = leader_agent.invoke({'messages':[{'role':'user',
                                               'content':prompt}]})
  code = response['messages'][-1].content[-1]['text']
  return code


#============== STEP 7 AGENT CALL==================
# leader_agent creation
leader_agent = create_agent(
    model = model,
    tools = [search_latest_info,
             generate_image]
)

#=================STEP 8 NAVBAR STREAMLIT================
tab1,tab2,tab3 = st.tabs(["Geneate Image",
                          "Fetch Latest News",
                          "Generate PPT"])

if (user_input) and (leader_agent):
  # TAB 1 code
  with tab1:
    if st.button("Generate Image", key = "Gen-Image"):
      with st.spinner("Running Agent"):
        try:
          generate_image(user_input)
          st.image(img)
        except:
          url = f"https://image.pollinations.ai/(user_input)"
          time.sleep(4)
          st.image(url)

  # TAB 1 code
  with tab2:
    if st.button("Fetch News", Key = "Fetch-News"):
      with st.spinner("Running Agent"):
        try:
          prompt = "Give Multiple news in HTML card Format for topic" + user_input
          response = leader_agent.invoke({'messages':[{'role':'user',
                                                       'content':prompt}]})
          code = response['messages'][-1].content[-1]['text']
          st.html(code, width="stretch",
                  unsafe_allow_javascript=True)
        except Exception as err:
          st.error(err)

  # TAB 3 code:
  with tab3:
    if st.button("Generate PPT", key = "gen-PPT"):
      with st.spinner("Running Agent"):
        try:
          code = run_agent(leader_agent,user_input)
          st.html(code, width="stretch",
              unsafe_allow_javascript=True)

          # File save
          with open("ppt.html",'w') as f:
            f.write(code)

          st.download_button(label = "DOWNLOAD PPT",
                         data = code,
                             file_name = 'ppt.html',
                             mime = 'text/html')

        except Exception as err:
          st.error(err)

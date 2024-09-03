import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from textwrap import dedent
from phi.assistant import Assistant
#from phi.tools.newspaper_toolkit import NewspaperToolkit
from phi.tools.newspaper4k import Newspaper4k
#from phi.tools.duckduckgo import DuckDuckGo
from phi.llm.openai import OpenAIChat
from st_copy_to_clipboard import st_copy_to_clipboard
#import base64

load_dotenv()

st.set_page_config(page_title="AI Journalist", page_icon="🗞️", layout="wide")

from utils.page_config import getlogo, page_config

getlogo()
page_config()

# Dummy credentials
USERNAME = os.getenv("APP_USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Fixed API key (replace with your actual API key)
FIXED_API_KEY = os.getenv("OPENAI_API_KEY")


# Create a simple login function
def login(username, password):
    return username == USERNAME and password == PASSWORD

article_guidelines = [
    "Inverted Pyramid: This is how you should organize your story. That means the most fundamental, important information (the “base” of the pyramid) goes up at the top, and information that is less crucial goes further down in the story.",
    "Lead: The start of a news story should present the most compelling information.",
    "Fact (Not Opinion) and Attribution: State the actual facts, figures, dates and numbers and always provide proper attribution.",
    "Identification: A person’s full first name or both initials should be used on first reference—not just a single initial. It shouldn’t be assumed that every reader knows who the person is; he or she should be identified in a way that’s relevant to the article.",
    "Short Paragraphs: In newswriting, paragraphs are kept short for punchiness and appearance.",
    "Headlines: Headlines should be short and preferably snappy. They should come out of information in the body of the text and not present new information."
    "Conclusion: Always end the article with a proper conclusion heading restating the premise."
]

editing_principles = [
    "Accuracy: Checking and crosschecking names, figures and verifying facts are of utmost importance.",
    "Attribution: Always attribute the news to the source so that readers can judge its credibility.",
    "Brevity:  It is telling a story, as it should be, without beating around the bush.",
    "Readability: The average length of a sentence should not exceed 18 words, which is standard. The best way is to write news stories using simple words, short and simple sentences.",
    "Explanatory or Analysis—still opinion, but mostly casts new light on ongoing issue.",
    "The editorial opens with power and closes with purpose. Begin with a premise or strongly worded opinion then wrap up with a conclusion that restates the premise. ",
    "In the body, provide facts, information and statistics to support your premise. ",
    " The facts (evidence) should be as complete as possible in the space allowed. Avoid repeating arguments in the body, even if using different language.",
    "Finish with a conclusion that restates the premise."
]
def main_app(api_key: str) -> None:
    """
    Main app function that generates an article using the AI Journalist.

    Args:
        api_key (str): The API key to use for accessing the OpenAI API.

    Returns:
        None
    """
    with st.container():
        st.title("AI Journalist🗞️")
        st.caption("Generate high-quality articles with AI Journalist by researching, writing, and editing articles using GPT-4o.")
    
    if st.button("Logout"):
        with open("click_log.txt", "a") as f:
            f.write(f"{datetime.datetime.now()}: {st.session_state.counter}\n")
        st.session_state.logged_in = False
        st.rerun()

    writer = Assistant(
        name="Writer",
        role="Retrieve text from URLs and write high-quality article",
        llm=OpenAIChat(model="gpt-4o", api_key=api_key, temperature=0),
        description=dedent(
            f"""
        You are a senior writer with a 20+ years of experience at the New York Times.
        Given a topic and a list of URLs,your goal is to write a high-quality NYT-worthy article on the topic using the information from the provided links.
        """
        ),
        instructions=[
            "Write a high-quality NYT-worthy article on the given topic within the word limit. Do not exceed the given word limit.",
            "People involved and mentioned in the text, places, dates, numbers, amounts, quotes, etc, all these things should be retained and must be mentioned in the final article."
            f"Curate the article based on the guidelines in the {article_guidelines}."
            "Write in proper headings/sections and subheadings/subsections.",
            "Ensure you provide a nuanced and balanced opinion, quoting facts where possible.",
            "Focus on clarity, coherence, and overall quality.",
            "Never make up facts or plagiarize. Always provide proper attribution.",
            "At the end of the article, Create a sources list of each result you cited, with the article name, author, and link."
        ],
        tools=[Newspaper4k(include_summary=True)],
        show_tool_calls=True,
        debug_mode=True,
        prevent_hallucinations=True,
    )

    editor = Assistant(
        name="Editor",
        team=[writer],
        llm=OpenAIChat(model="gpt-4o", api_key=api_key, temperature=0),
        role="Get the draft of the article from writer and edit it as per the given instructions.",
        description="You are a senior NYT editor. Given a topic, your goal is to write a NYT-worthy article.",
        instructions=[
            "Given a topic, URLs and word limit, pass the description of the topic and URLs to the writer to get a draft of the article.",
            #f"Format the article based on the guidelines in the {editing_principles}."
            "Edit, proofread, and refine the article to ensure it meets the high standards of the New York Times.",
            "The article should be extremely articulate and well-written.",
            "Focus on clarity, coherence, and overall quality.",
            "Ensure the article is engaging and informative."
        ],
        add_datetime_to_instructions=True,
        markdown=True,
        debug_mode=True
    )
    
    response = ""
    # Input field for the report query
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.header("Input & Configuration")
            query: str = st.text_input("What do you want the AI journalist to write an article on?", placeholder="E.g: Emergence of AI and LLMs.")
            
            word_limit: int = st.slider("How long should be your article?", min_value=250, max_value=1500, step=50, key="word_limit")

            use_links = st.radio("Do you want to provide reference links?", ("No", "Yes"))

            links: List[str] = []
            if use_links == "Yes":
                    num_links: int = st.number_input("How many links do you want to provide?",placeholder="Enter the number of links that you want to use", min_value=1, max_value=5, step=1, key="number_of_links", help="These links will be used to curate your news article.")
                    for i in range(num_links):
                        link: str = st.text_input(f"Enter reference link {i+1}", key=f"link_{i+1}")
                        links.append(link)
                        
            # Create a counter to count the number of clicks on 'Generate Article'

            if use_links == "No" or (use_links == "Yes" and all(links)):
                    if st.button("Generate Article"):
                        st.session_state.counter += 1
                        if query:
                            with st.spinner("Good things take time, and we're making sure it's perfect for you!"):
                        # Prepare the content for the writer
                                links_text = "\n".join(links) if links else "No reference links provided."
                                writer_instructions = f"Topic: {query}\nReference Links:\n{links_text}\nWord Limit:{word_limit}"

                        # Get the response from the assistant
                                response = editor.run(writer_instructions, stream=False)
                                print("WRITER METRICS: \n")
                                print(writer.llm.metrics)
                                print("EDITOR METRICS: \n")
                                print(editor.llm.metrics)
                        else:
                            st.error("Please provide a topic to write an article on.")
            
    with col2:
        with st.container(border=True):
            if not response == "":
                st.markdown(response)
                st_copy_to_clipboard(response)
            else:
                with st.container():
                    st.image("stock.png", width=350, caption="Your generated article will be displayed here.")
                
spacer_left, form, spacer_right = st.columns([1,1,1], vertical_alignment="bottom")

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        if "counter" not in st.session_state:
            st.session_state.counter = 0
        main_app(FIXED_API_KEY)
    else:
        with form:
            with st.container(border=True):
                st.title("Login")

                # Create login form
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")

                if st.button("Login", use_container_width=True):
                    if login(username, password):
                        st.session_state.logged_in = True
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
    
    
if __name__ == "__main__":
    main()


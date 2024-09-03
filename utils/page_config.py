import streamlit as st
import base64

def getlogo():
    with open("logo.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return st.markdown(
        f"""
        <div style="position:fixed;
        display:flex;
        align-items:center;
        top:2%;
        background-color: rgb(14, 17, 23);
        z-index:10;
        margin-left:auto;">
            <img src="data:image/webp;base64,{data}" width="150" height="60">
        </div>
        """,
        unsafe_allow_html=True,
    )
    
def page_config():
    return st.markdown("""
            <style>
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
            
            header[data-testid="stHeader"] {
                background:transparent;
            }
            div[class="block-container st-emotion-cache-1jicfl2 ea3mdgi5"] {
                margin-top:5%;
                padding-top:5%;
            }
            
            h1[id="d88c5d7a"], div[class="st-emotion-cache-fmhvvr e1nzilvr4"] > p {
                text-align:center;
            }
            
            div[class="st-emotion-cache-1v0mbdj e115fcil1"] {
                display: flex;
                flex-direction:column;
                height:auto;
                padding:0.7%;
                margin:auto;
                justify-content: center;
                align-items: center;
            }
            </style>
            """, unsafe_allow_html=True)
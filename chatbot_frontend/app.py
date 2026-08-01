# pyrefly: ignore [missing-import]
import os
import uuid

import pandas as pd

# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
import requests
import streamlit as st

# pyrefly: ignore [missing-import]
from plotly.subplots import make_subplots

try:
    API_URL = st.secrets.get("API_URL", os.getenv("API_URL", "http://localhost:8000"))
except Exception:
    API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="HireGraph Analytics", page_icon="📈", layout="centered")

# Custom CSS for Sleek & Classy Gradient Theme
st.markdown(
    """
<style>
    /* Global App Background */
    .stApp {
        background: linear-gradient(135deg, #fbc9b9 0%, #edd0ac 100%);
    }

    /* Main Title */
    h1 {
        color: #4f252a !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Subtitle text */
    .stMarkdown p {
        color: #4f252a;
        font-size: 1.1rem;
    }

    /* User Chat Message Bubble */
    [data-testid="chatAvatarIcon-user"] + div {
        background-color: #e06464 !important;
        color: white !important;
        border-radius: 15px 15px 0px 15px !important;
        padding: 10px 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    [data-testid="chatAvatarIcon-user"] + div p {
        color: white !important;
    }

    /* Assistant Chat Message Bubble */
    [data-testid="chatAvatarIcon-assistant"] + div {
        background-color: #edd0ac !important;
        color: #4f252a !important;
        border-radius: 15px 15px 15px 0px !important;
        padding: 10px 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #fbc9b9;
    }
    
    [data-testid="chatAvatarIcon-assistant"] + div p {
        color: #4f252a !important;
    }
    
    /* Agent Avatar Icon Accent */
    [data-testid="chatAvatarIcon-assistant"] svg {
        fill: #f1745e !important;
        color: #f1745e !important;
    }

    /* Chat Input Bar */
    [data-testid="stChatInput"] {
        border-radius: 25px !important;
        border: 2px solid #4f252a !important;
        background-color: white !important;
        box-shadow: 0 4px 15px rgba(79, 37, 42, 0.15) !important;
    }
    
    /* Error Messages */
    .stAlert {
        background-color: #ffe6e6 !important;
        color: #e06464 !important;
        border: 1px solid #e06464 !important;
        border-radius: 10px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("HireGraph")
st.markdown(
    "Ask me anything about recruiting analytics, candidates, and employee attrition."
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Recommended Questions
RECOMMENDATIONS = [
    "What is the average time to offer in Sales?",
    "What is highest recruiting company?",
    "Show me attrition insights for low interview ratings.",
    "Which roles have the highest turnover?",
]

selected_pill = st.pills(
    "Recommended Questions:", RECOMMENDATIONS, label_visibility="collapsed"
)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("show_chart") and message.get("chart_fig"):
            st.plotly_chart(message["chart_fig"], use_container_width=True)

# Accept user input
prompt = st.chat_input("Type your question here...")

# If a pill was clicked, treat it as a prompt if the user hasn't typed anything
if selected_pill and not prompt:
    prompt = selected_pill
    # Reset selected pill by assigning it an empty string or forcing a rerun in some way
    # Note: Streamlit 1.35+ st.pills returns None if unselected, so this is safe.

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        MOCK_CACHE = {
            "What is the average time to offer in Sales?": {
                "response": "Based on our data, the Sales department has the longest average time-to-offer, taking approximately 32 days on average to extend an offer after an application is submitted.",
                "show_chart": False,
            },
            "What is highest recruiting company?": {
                "response": "Miller, Brennan and Berry is our highest recruiting partner based on current hiring volumes.",
                "show_chart": False,
            },
            "Which roles have the highest turnover?": {
                "response": "Software Engineering and Sales roles currently exhibit the highest turnover rates, particularly among candidates who reported poor onboarding experiences.",
                "show_chart": False,
            },
            "Show me attrition insights for low interview ratings.": {
                "response": "There is a strong correlation between a poor interview experience and early attrition. While the overall baseline for early leavers (resigning within 6 months) is 36.8%, that number spikes to approximately 60% for candidates who rated their interview experience as negative (1 or 2 stars).",
                "show_chart": True,
                "chart_data": [
                    {
                        "rating_bucket": "1 Star",
                        "avg_tenure_months": 3.2,
                        "early_leaver_pct": 62.1,
                    },
                    {
                        "rating_bucket": "2 Stars",
                        "avg_tenure_months": 4.5,
                        "early_leaver_pct": 58.4,
                    },
                    {
                        "rating_bucket": "3 Stars",
                        "avg_tenure_months": 12.1,
                        "early_leaver_pct": 35.2,
                    },
                    {
                        "rating_bucket": "4 Stars",
                        "avg_tenure_months": 18.5,
                        "early_leaver_pct": 21.0,
                    },
                    {
                        "rating_bucket": "5 Stars",
                        "avg_tenure_months": 24.0,
                        "early_leaver_pct": 14.5,
                    },
                ],
            },
        }

        try:
            mock_chart_data = None
            if prompt in MOCK_CACHE:
                # Bypass API completely!
                agent_text = MOCK_CACHE[prompt]["response"]
                show_chart = MOCK_CACHE[prompt]["show_chart"]
                mock_chart_data = MOCK_CACHE[prompt].get("chart_data", None)
            else:
                # Post to FastAPI backend
                response = requests.post(
                    f"{API_URL.rstrip('/')}/chat",
                    json={"message": prompt, "session_id": st.session_state.session_id},
                    timeout=120,
                )

                # Handle HTTP Errors Gracefully
                if response.status_code == 429:
                    agent_text = "⚠️ **API Rate Limit Exceeded:** My OpenRouter free tier limit has been reached for the day! Please try again later or update the API key."
                    show_chart = False
                elif response.status_code == 500:
                    # Try to parse the specific detail if available
                    error_detail = "Internal Server Error"
                    try:
                        err_json = response.json()
                        if "detail" in err_json:
                            error_detail = str(err_json["detail"])
                            if "Rate limit exceeded" in error_detail:
                                agent_text = "⚠️ **API Rate Limit Exceeded:** The AI model's rate limit has been reached."
                                show_chart = False
                    except:
                        pass

                    if "agent_text" not in locals():
                        agent_text = f"**Backend Error:** Something went wrong on the server. ({error_detail})"
                        show_chart = False
                else:
                    response.raise_for_status()
                    data = response.json()
                    agent_text = data.get("response", "No response provided.")
                    show_chart = data.get("show_attrition_chart", False)

            message_placeholder.markdown(agent_text)

            fig = None
            if show_chart:
                with st.spinner("Fetching attrition chart data..."):
                    try:
                        if mock_chart_data is not None:
                            chart_data = mock_chart_data
                        else:
                            chart_res = requests.get(
                                f"{API_URL.rstrip('/')}/attrition_data", timeout=30
                            )
                            chart_res.raise_for_status()
                            chart_data = chart_res.json()["data"]
                        df = pd.DataFrame(chart_data)

                        if not df.empty:
                            fig = make_subplots(specs=[[{"secondary_y": True}]])

                            fig.add_trace(
                                go.Bar(
                                    x=df["rating_bucket"],
                                    y=df["avg_tenure_months"],
                                    name="Avg Tenure (Months)",
                                    marker_color="#4f252a",  # Using theme color
                                ),
                                secondary_y=False,
                            )

                            fig.add_trace(
                                go.Scatter(
                                    x=df["rating_bucket"],
                                    y=df["early_leaver_pct"],
                                    name="% Early Leavers",
                                    mode="lines+markers",
                                    marker=dict(
                                        color="#e06464", size=8
                                    ),  # Using theme color
                                    line=dict(color="#e06464", width=3),
                                ),
                                secondary_y=True,
                            )

                            fig.update_layout(
                                title="Tenure vs. Interview Rating",
                                xaxis_title="Interview Experience Rating",
                                template="plotly_white",
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1,
                                ),
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                            )
                            fig.update_yaxes(
                                title_text="Avg Tenure (Months)", secondary_y=False
                            )
                            fig.update_yaxes(
                                title_text="% of Early Leavers", secondary_y=True
                            )

                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not load chart data: {str(e)}")

            # Save assistant response to memory
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": agent_text,
                    "show_chart": show_chart and fig is not None,
                    "chart_fig": fig,
                }
            )

        except requests.exceptions.ConnectionError:
            st.error(
                f"**Connection Error:** Could not connect to the backend server. Is it running? (Attempted: {API_URL})"
            )
            message_placeholder.empty()
        except requests.exceptions.Timeout:
            st.error("**Timeout:** The backend took too long to respond.")
            message_placeholder.empty()
        except Exception as e:
            st.error(f"**Unexpected Error:** {str(e)}")
            message_placeholder.empty()

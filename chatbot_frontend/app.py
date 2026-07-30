import streamlit as st
import requests
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

API_URL = "http://localhost:8000"

st.set_page_config(page_title="HireGraph Analytics", page_icon="📈", layout="centered")

st.title("HireGraph")
st.markdown("Ask me anything about recruiting analytics, candidates, and employee attrition.")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("show_chart"):
            st.plotly_chart(message["chart_fig"], use_container_width=True)

# Accept user input
if prompt := st.chat_input("E.g., What is the average time to offer in Sales?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Post to FastAPI backend
            response = requests.post(
                f"{API_URL}/chat", 
                json={"message": prompt, "session_id": st.session_state.session_id},
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            
            agent_text = data["response"]
            show_chart = data.get("show_attrition_chart", False)
            
            message_placeholder.markdown(agent_text)
            
            fig = None
            if show_chart:
                with st.spinner("Fetching attrition chart data..."):
                    chart_res = requests.get(f"{API_URL}/attrition_data")
                    if chart_res.status_code == 200:
                        chart_data = chart_res.json()["data"]
                        df = pd.DataFrame(chart_data)
                        
                        if not df.empty:
                            # Create a dual-axis chart
                            fig = make_subplots(specs=[[{"secondary_y": True}]])
                            
                            # Add bar chart for Avg Tenure
                            fig.add_trace(
                                go.Bar(
                                    x=df['rating_bucket'],
                                    y=df['avg_tenure_months'],
                                    name="Avg Tenure (Months)",
                                    marker_color='rgb(55, 83, 109)'
                                ),
                                secondary_y=False,
                            )
                            
                            # Add line chart for Early Leaver %
                            fig.add_trace(
                                go.Scatter(
                                    x=df['rating_bucket'],
                                    y=df['early_leaver_pct'],
                                    name="% Early Leavers (vs total early leavers)",
                                    mode='lines+markers',
                                    marker=dict(color='rgb(219, 64, 82)', size=8),
                                    line=dict(color='rgb(219, 64, 82)', width=3)
                                ),
                                secondary_y=True,
                            )
                            
                            fig.update_layout(
                                title="Tenure vs. Interview Rating",
                                xaxis_title="Interview Experience Rating",
                                template="plotly_white",
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )
                            fig.update_yaxes(title_text="Avg Tenure (Months)", secondary_y=False)
                            fig.update_yaxes(title_text="% of Early Leavers", secondary_y=True)
                            
                            st.plotly_chart(fig, use_container_width=True)
            
            # Save assistant response to memory
            st.session_state.messages.append({
                "role": "assistant", 
                "content": agent_text,
                "show_chart": show_chart and fig is not None,
                "chart_fig": fig
            })
            
        except Exception as e:
            message_placeholder.markdown(f"**Error:** {str(e)}")

import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import json


class DisplayResultStreamlit:
    def __init__(self,usecase,graph,user_message):
        self.usecase= usecase
        self.graph = graph
        self.user_message = user_message
        

    def display_result_on_ui(self):
        usecase= self.usecase
        graph = self.graph
        user_message = self.user_message
        print(user_message)

        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []


        if usecase == "Basic Chatbot":
            #  Add user message to history
            st.session_state["chat_history"].append(
                HumanMessage(content=user_message)
            )
            #  Limit history 
            st.session_state["chat_history"] = st.session_state["chat_history"][-6:]

            # Invoke graph with full history
            res = graph.invoke({
                "messages": st.session_state["chat_history"]
            })
            #  Extract AI response
            ai_response = None
            for message in res["messages"]:
                if isinstance(message, AIMessage) and message.content:
                    ai_response = message.content
            #  Add AI response to history
            if ai_response:
                st.session_state["chat_history"].append(
                    AIMessage(content=ai_response)
                )
            # Display full chat history (clean UI)
            for msg in st.session_state["chat_history"]:
                if isinstance(msg, HumanMessage):
                    with st.chat_message("user"):
                        st.markdown(msg.content)

                elif isinstance(msg, AIMessage):
                    with st.chat_message("assistant"):
                        st.markdown(msg.content)




        elif usecase == "Chatbot With Web":
            # Add user message
            st.session_state["chat_history"].append(
                HumanMessage(content=user_message)
            )
            # Limit history (important)
            st.session_state["chat_history"] = st.session_state["chat_history"][-6:]
            # Invoke graph with history
            res = graph.invoke({
                "messages": st.session_state["chat_history"]
            })

            # Extract AI response
            ai_response = None

            for message in res['messages']:

                if isinstance(message, ToolMessage):
                    # showing tool usage
                    with st.chat_message("assistant"):
                        st.markdown("🔧 *Using tool...*")

                elif isinstance(message, AIMessage) and message.content:
                    ai_response = message.content

            # Adding AI response to history
            if ai_response:
                st.session_state["chat_history"].append(
                    AIMessage(content=ai_response)
                )

            # Display full chat history
            for msg in st.session_state["chat_history"]:

                if isinstance(msg, HumanMessage):
                    with st.chat_message("user"):
                        st.markdown(msg.content)

                elif isinstance(msg, AIMessage):
                    with st.chat_message("assistant"):
                        st.markdown(msg.content)




        

        elif usecase == "AI News":

            frequency = self.user_message
            # Add user message
            st.session_state["chat_history"].append(
                HumanMessage(content=f"Show {frequency} AI news")
            )

            # Limit history
            st.session_state["chat_history"] = st.session_state["chat_history"][-6:]

            with st.spinner("Fetching and summarizing news... ⏳"):

                # Invoke graph (no need history inside graph for this usecase)
                graph.invoke({"messages": frequency})
                try:
                    AI_NEWS_PATH = f"./AINews/{frequency.lower()}_summary.md"
                    with open(AI_NEWS_PATH, "r") as file:
                        markdown_content = file.read()
                    # Add response to history
                    st.session_state["chat_history"].append(
                        AIMessage(content=markdown_content)
                    )

                except FileNotFoundError:
                    st.error(f"News Not Generated or File not found: {AI_NEWS_PATH}")
                    return

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    return

            # 🔷 Display full chat history (clean UI)
            for msg in st.session_state["chat_history"]:

                if isinstance(msg, HumanMessage):
                    with st.chat_message("user"):
                        st.markdown(msg.content)

                elif isinstance(msg, AIMessage):
                    with st.chat_message("assistant"):
                        st.markdown(msg.content, unsafe_allow_html=True)








        elif usecase == "AI Research Assistant":
            # Add user message
            st.session_state["chat_history"].append(
                HumanMessage(content=user_message)
            )

            # Limit history 
            st.session_state["chat_history"] = st.session_state["chat_history"][-6:]

            # Invoke graph with full history
            res = graph.invoke({
                "messages": st.session_state["chat_history"]
            })

            # Extract final AI response
            ai_response = None
            for message in res['messages']:
                if isinstance(message, AIMessage) and message.content:
                    ai_response = message.content.strip()

            # Add AI response to history
            if ai_response:
                st.session_state["chat_history"].append(
                    AIMessage(content=ai_response)
                )

            st.empty()

            # Display full chat history
            for msg in st.session_state["chat_history"]:

                if isinstance(msg, HumanMessage):
                    with st.chat_message("user"):
                        st.markdown(msg.content, unsafe_allow_html=False)

                elif isinstance(msg, AIMessage):
                    with st.chat_message("assistant"):
                        st.markdown(msg.content, unsafe_allow_html=False)
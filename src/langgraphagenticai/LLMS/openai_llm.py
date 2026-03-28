import os
import streamlit as st
from langchain_openai import ChatOpenAI

class OpenAILLM:
    def __init__(self, user_contols_input):
        self.user_controls_input = user_contols_input

    def get_llm_model(self):
        try:
            openai_api_key = self.user_controls_input.get("OPENAI_API_KEY")
            selected_openai_model = self.user_controls_input.get("selected_openai_model")

            if not openai_api_key and not os.environ.get("OPENAI_API_KEY"):
                st.error("Please enter the OpenAI API key")
                return None

            llm = ChatOpenAI(
                api_key=openai_api_key,
                model=selected_openai_model
            )

        except Exception as e:
            raise ValueError(f"Error occurred: {e}")

        return llm
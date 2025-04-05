import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("🍳 요리 도우미 챗봇")
st.write(
    "냉장고에 있는 재료를 알려주면 맛있는 레시피를 제안해드려요! "
    "요리 과정도 단계별로 안내하고, 궁금한 점이 있으면 언제든 물어보세요. "
    "이 앱을 사용하려면 OpenAI API 키가 필요합니다. [여기](https://platform.openai.com/account/api-keys)에서 얻을 수 있어요."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "당신은 요리 도우미 챗봇입니다. 사용자가 입력한 재료를 기반으로 레시피를 제안하거나, 요리 과정을 단계별로 안내해주세요. 자연스럽고 친절한 한국어로 대답하세요."}
        ]

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        if message["role"] != "system":  # 시스템 메시지는 표시하지 않음
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message.
    if prompt := st.chat_input("냉장고에 양파랑 고기밖에 없는데, 뭐 만들 수 있을까?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

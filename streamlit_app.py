import streamlit as st
from openai import OpenAI
import pandas as pd

# Show title and description.
st.title("🍳 요리 도우미 챗봇")
st.write(
    "냉장고에 있는 재료를 표에 입력하면 맛있는 레시피를 제안해드려요! "
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
            {"role": "system", "content": "당신은 요리 도우미 챗봇입니다. 재료 부분은 표 형식으로 만들어주렴. 요리 과정을 단계별로 안내해주세요. 자연스럽고 친절한 한국어로 대답하세요."}
        ]

    # 재료 입력을 위한 표 생성
    st.subheader("냉장고 재료 입력")
    if "ingredients_df" not in st.session_state:
        st.session_state.ingredients_df = pd.DataFrame(
            {"재료": ["", "", ""], "수량": ["", "", ""]}
        )

    # 동적 표 편집기
    edited_df = st.data_editor(
        st.session_state.ingredients_df,
        num_rows="dynamic",  # 행 추가/삭제 가능
        column_config={
            "재료": st.column_config.TextColumn("재료", help="재료 이름을 입력하세요 (예: 양파, 고기)"),
            "수량": st.column_config.TextColumn("수량", help="수량을 입력하세요 (예: 1개, 200g)")
        },
        key="ingredients_table"
    )

    # 표 데이터를 세션 상태에 저장
    st.session_state.ingredients_df = edited_df

    # "레시피 제안받기" 버튼 추가
    if st.button("레시피 제안받기"):
        # 표에서 입력된 재료를 문자열로 변환
        ingredients_list = [
            f"{row['재료']} {row['수량']}".strip()
            for _, row in edited_df.iterrows()
            if row["재료"] and row["수량"]  # 빈 값 제외
        ]
        if ingredients_list:
            prompt = f"냉장고에 {', '.join(ingredients_list)}가 있어. 뭐 만들 수 있을까?"
        else:
            prompt = "재료를 입력해주세요!"

        # 사용자 메시지 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI API로 응답 생성
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # 응답 스트리밍 및 저장
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 기존 채팅 메시지 표시
    st.subheader("대화 기록")
    for message in st.session_state.messages:
        if message["role"] != "system":  # 시스템 메시지는 표시하지 않음
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 추가 질문 입력 필드
    if prompt := st.chat_input("요리 과정이나 다른 질문이 있으면 물어보세요!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

import streamlit as st
import json
import openai

# --- 页面配置 ---
st.set_page_config(page_title="Film Character Chatbox", page_icon="🎬", layout="centered")

st.title("🎬 Film Character Chatbox")
st.write("Talk to the characters from our Eastern European cinema class!")

# --- 1. 获取 OpenAI API Key ---
# 它是从 Streamlit Secrets 里读取的，这样比较安全
try:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ OpenAI API Key missing! Please set 'OPENAI_API_KEY' in Streamlit Secrets.")
    st.stop()

# --- 2. 加载角色数据 ---
if "character_data" not in st.session_state:
    # 默认给一个测试角色，防止一开始空荡荡的不好看
    st.session_state.character_data = {
        "Test Character": "You are a helpful assistant testing the system."
    }

st.sidebar.header("Upload Character Data")
st.sidebar.info("Paste your JSON format character bios here.")
# 稍微把默认高度调大一点
user_json = st.sidebar.text_area("Character JSON", height=150, value=json.dumps(st.session_state.character_data, indent=2))

if st.sidebar.button("Load Characters"):
    try:
        st.session_state.character_data = json.loads(user_json)
        st.sidebar.success("Characters loaded successfully!")
        # 强制刷新一下页面以更新下拉菜单
        st.rerun() 
    except Exception as e:
        st.sidebar.error(f"Invalid JSON: {e}")

characters = list(st.session_state.character_data.keys())

if not characters:
    st.warning("Please upload character data in the sidebar to start.")
else:
    # --- 3. 选择角色 ---
    selected = st.selectbox("Choose a character to talk to:", characters)
    st.markdown(f"### Talking to: **{selected}**")

    # --- 4. 聊天记录管理 ---
    # 如果切换了角色，清空历史记录，不然会串戏
    if "last_selected" not in st.session_state or st.session_state.last_selected != selected:
        st.session_state.messages = []
        st.session_state.last_selected = selected

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示历史消息
    for m in st.session_state.messages:
        role, text = m
        if role == "user":
            st.chat_message("user").write(text)
        else:
            st.chat_message("assistant").write(text)

    # --- 5. 用户输入与 GPT 回复 ---
    if user_input := st.chat_input("Your message"):
        # 显示用户输入
        st.session_state.messages.append(("user", user_input))
        st.chat_message("user").write(user_input)

        # 准备发给 GPT 的 prompt
        notes = st.session_state.character_data[selected]
        
        # 构建消息列表：系统设定 + 历史记录 + 当前问题
        gpt_messages = [
            {"role": "system", "content": f"You are {selected}. Here is your character profile: {notes}. \nIMPORTANT: Stay in character fully. Do not mention you are an AI."},
        ]
        
        # 把历史记录加进去，这样它能记得上下文
        for role, text in st.session_state.messages:
            gpt_messages.append({"role": role, "content": text})

        # 调用 OpenAI API
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo", # 或者用 "gpt-4" 如果你的Key支持
                    messages=gpt_messages,
                    stream=True,
                )
                
                # 流式输出 (打字机效果)
                response = st.write_stream(stream)
                
                # 保存回复到历史
                st.session_state.messages.append(("assistant", response))
                
            except Exception as e:
                st.error(f"Error calling OpenAI API: {e}")

# --- Footer ---
st.markdown("---")
st.caption("Powered by OpenAI GPT-3.5 Turbo")

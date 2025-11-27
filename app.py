import streamlit as st
import json

st.set_page_config(page_title="Film Character Chatbox", page_icon="🎬", layout="centered")

st.title("🎬 Film Character Chatbox")
st.write("Talk to the characters from our Eastern European cinema class!")

# --- Load character data (user will paste JSON later) ---
if "character_data" not in st.session_state:
    st.session_state.character_data = {}

st.sidebar.header("Upload Character Data")
user_json = st.sidebar.text_area("Paste your character JSON here", height=200)
if st.sidebar.button("Load Characters"):
    try:
        st.session_state.character_data = json.loads(user_json)
        st.sidebar.success("Characters loaded successfully!")
    except:
        st.sidebar.error("Invalid JSON — please check formatting.")

characters = list(st.session_state.character_data.keys())

if not characters:
    st.warning("Please upload character data in the sidebar to start.")
else:
    # --- Select character ---
    selected = st.selectbox("Choose a character to talk to:", characters)
    st.markdown(f"### Talking to: **{selected}**")

    # --- Chat state ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for m in st.session_state.messages:
        role, text = m
        if role == "user":
            st.chat_message("user").write(text)
        else:
            st.chat_message("assistant").write(text)

    # --- User input ---
    user_input = st.chat_input("Your message")
    if user_input:
        st.session_state.messages.append(("user", user_input))
        st.chat_message("user").write(user_input)

        # Generate reply based on uploaded character notes
        notes = st.session_state.character_data[selected]

        # VERY SIMPLE character-based expansion logic
        reply = f"(As {selected}) {notes}\n\nResponding to what you said: {user_input}"

        st.session_state.messages.append(("assistant", reply))
        st.chat_message("assistant").write(reply)

# --- Footer ---
st.markdown("---")
st.write("Upload your character descriptions as JSON, e.g.:\n```
{
  \"Character Name\": \"Short personality description...\",
  \"Another Character\": \"Description...\"
}
```")

import streamlit as st

# Simple one-page SMS sharer
st.title("📲 Share App Link")
st.markdown("---")

app_url = "https://app1-pkgk.onrender.com/"

st.subheader("App Link:")
st.write(app_url)

st.subheader("Quick Share:")
phone = st.text_input("Enter phone number:", key="phone")

if phone:
    message = f"Check out this app: {app_url}"
    sms_url = f"sms:{phone}?body={message}"
    
    st.markdown(f'<a href="{sms_url}" target="_blank"><button style="background-color:green;color:white;padding:10px;border:none;border-radius:5px;">Send SMS</button></a>', unsafe_allow_html=True)

st.markdown("---")
st.info("💡 The SMS button will open your phone's messaging app with the link pre-filled.")
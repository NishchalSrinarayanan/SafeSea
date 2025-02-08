import streamlit as st

# Function to display the background image
def display_background(image_path):
    st.markdown(
        f"""
        <style>
        .main {{
            background-image: url("{image_path}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: white; /* Text color for better contrast */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Main app ---
st.set_page_config(page_title="SafeSea", page_icon=":ocean:")  # Set title and icon

# Replace 'your_image.png' with the actual path to your image file
image_path = "safeseatitle.png"  # Make sure the image is in the same directory as the script or provide the full path
display_background(image_path)

# --- Home Page ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    st.title("Welcome to SafeSea")
    
    col1, col2 = st.columns(2)  # Create two columns for buttons
    
    if col1.button("I am a Sailor"):
        st.session_state.page = 'sailor_checkin'
    if col2.button("I am a Diver"):
        st.session_state.page = 'diver_checkin'  # You'll need to create this page


# --- Sailor Check-in Page ---
elif st.session_state.page == 'sailor_checkin':
    st.title("Sailor Check-in")
    # Add your check-in form/logic here
    st.write("Please enter your details:")
    sailor_name = st.text_input("Name")
    # ... other input fields ...
    if st.button("Submit Check-in"):
        # Process the check-in data (e.g., store in a database or file)
        st.write(f"Thank you, {sailor_name}! Your check-in is complete.")
        st.session_state.page = 'home'  # Go back to the home page after check-in


# --- Diver Check-in Page (Placeholder) ---
elif st.session_state.page == 'diver_checkin':
    st.title("Diver Check-in (Coming Soon!)")
    st.write("This page is under development.")
    if st.button("Go Back"):
        st.session_state.page = 'home'

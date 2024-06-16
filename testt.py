import streamlit as st

def main():
    st.title("Welcome to Streamlit")
    st.header("This is a simple Streamlit app!")
    st.subheader("Try changing the value below:")
    
    name = st.text_input("Enter your name", "John Doe")
    st.write("Hello,", name, "!")

if __name__ == '__main__':
    main()

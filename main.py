import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Sentiment Analysis System", page_icon="https://cdn-icons-png.flaticon.com/512/9850/9850903.png")
st.title("Sentiment Analysis System")

choice = st.sidebar.selectbox("My Menu", ("HOME", "ANALYSIS", "RESULTS"))

if choice == "HOME":
    st.image("https://media.sproutsocial.com/uploads/2023/07/Sentiment-analysis-HUB-Final.jpg")
    st.write("1. It is a Natural Language Processing Application which can analyze the sentiment on text data.")
    st.write("2. This application predicts the sentiment into 3 categories: Positive, Negative, Neutral.")
    st.write("3. This application then visualizes the results based on different factors such as age, gender, language, city.")
elif choice == "ANALYSIS":
    sid = st.text_input("Enter your Google Sheet ID")
    r = st.text_input("Enter Range between first column and last column")
    c = st.text_input("Enter column name that is to be analyzed")
    btn = st.button("Analyze")
    if btn:
        try:
            if 'cred' not in st.session_state:
                f = InstalledAppFlow.from_client_secrets_file("key.json", ["https://www.googleapis.com/auth/spreadsheets"])
                st.session_state['cred'] = f.run_local_server(port=0)

            service = build("Sheets", "v4", credentials=st.session_state['cred']).spreadsheets().values()
            k = service.get(spreadsheetId=sid, range=r).execute()
            d = k['values']
            df = pd.DataFrame(data=d[1:], columns=d[0])
            
            st.write("Data loaded successfully")
            st.write(df.head())

            l = []
            mymodel = SentimentIntensityAnalyzer()
            for i in range(len(df)):
                t = df._get_value(i, c)
                pred = mymodel.polarity_scores(t)
                if pred['compound'] > 0.5:
                    l.append("positive")
                elif pred['compound'] < -0.5:
                    l.append("negative")
                else:
                    l.append("neutral")
            df['Sentiment'] = l
            
            df.to_csv("results.csv", index=False)
            st.subheader("The analysis results are saved as results.csv")
            st.write("results.csv created successfully")
        except Exception as e:
            st.error(f"An error occurred: {e}")
elif choice == "RESULTS":
    if os.path.exists("results.csv"):
        df = pd.read_csv("results.csv")
        choice2 = st.selectbox("Choose Visualization", ("NONE", "PIE CHART", "HISTOGRAM", "SCATTER PLOT"))
        st.dataframe(df)
        
        if choice2 == "PIE CHART":
            posper = (len(df[df['Sentiment'] == 'positive']) / len(df)) * 100
            negper = (len(df[df['Sentiment'] == 'negative']) / len(df)) * 100
            neuper = (len(df[df['Sentiment'] == 'neutral']) / len(df)) * 100
            fig = px.pie(values=[posper, negper, neuper], names=["positive", "negative", "neutral"])
            st.plotly_chart(fig)
        elif choice2 == "HISTOGRAM":
            k = st.selectbox("Choose column", df.columns)
            if k:
                fig = px.histogram(x=df[k], color=df['Sentiment'])
                st.plotly_chart(fig)
        elif choice2 == "SCATTER PLOT":
            k = st.text_input("Enter the continuous column name")
            if k:
                fig = px.scatter(x=df[k], y=df['Sentiment'])
                st.plotly_chart(fig)
    else:
        st.error("The results file does not exist. Please run the analysis first.")

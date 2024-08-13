import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

def authenticate():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('key.json', SCOPES)
            creds = flow.run_console()  # Use run_console for headless environments
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    return creds

st.title("Sentiment Analysis System")

choice = st.sidebar.selectbox("My Menu", ("HOME", "ANALYSIS", "RESULTS"))

if choice == "ANALYSIS":
    sid = st.text_input("Enter your Google Sheet ID")
    r = st.text_input("Enter Range between first column and last column")
    c = st.text_input("Enter column name that is to be analyzed")
    btn = st.button("Analyze")
    
    if btn:
        try:
            creds = authenticate()
            service = build('sheets', 'v4', credentials=creds).spreadsheets().values()
            k = service.get(spreadsheetId=sid, range=r).execute()
            d = k['values']
            df = pd.DataFrame(data=d[1:], columns=d[0])
            
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

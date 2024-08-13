import streamlit as st 
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import pandas as pd
import plotly.express as px 
import webbrowser

# Register Chrome browser (update path as necessary)
chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Corrected path
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

st.set_page_config(page_title="Sentiment Analysis System", page_icon="https://cdn-icons-png.flaticon.com/512/9850/9850903.png")
st.title("Sentiment Analysis System")

choice = st.sidebar.selectbox("My Menu", ("HOME", "ANALYSIS", "RESULTS"))

if choice == "HOME":
    st.image("https://media.sproutsocial.com/uploads/2023/07/Sentiment-analysis-HUB-Final.jpg")
    st.write("1. This is a Natural Language Processing application that can analyze sentiment from text data.")
    st.write("2. It categorizes sentiment into Positive, Negative, or Neutral.")
    st.write("3. The application visualizes results based on factors such as age, gender, language, and city.")

elif choice == "ANALYSIS":
    sid = st.text_input("Enter your Google Sheet ID")
    r = st.text_input("Enter Range (e.g., Sheet1!A1:D100)")
    c = st.text_input("Enter column name to be analyzed")
    
    if st.button("Analyze"):
        if 'cred' not in st.session_state:
            try:
                # Initialize OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'key.json',
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                
                # Run local server for authentication
                st.session_state['cred'] = flow.run_local_server(port=0, browser='chrome')
            except Exception as e:
                st.error(f"An error occurred during authentication: {e}")
                st.stop()
        
        try:
            # Build the Google Sheets API service
            service = build("sheets", "v4", credentials=st.session_state['cred']).spreadsheets().values()
            result = service.get(spreadsheetId=sid, range=r).execute()
            data = result.get('values', [])
            
            if not data:
                st.error("No data found in the provided range.")
            else:
                df = pd.DataFrame(data[1:], columns=data[0])
                if c not in df.columns:
                    st.error(f"Column '{c}' not found in the data.")
                else:
                    # Perform sentiment analysis
                    analyzer = SentimentIntensityAnalyzer()
                    df['Sentiment'] = df[c].apply(lambda x: "positive" if analyzer.polarity_scores(x)['compound'] > 0.5 else 
                                                       "negative" if analyzer.polarity_scores(x)['compound'] < -0.5 else "neutral")
                    df.to_csv("results.csv", index=False)
                    st.success("Analysis results are saved as 'results.csv'")
        
        except Exception as e:
            st.error(f"An error occurred while processing the data: {e}")

elif choice == "RESULTS":
    try:
        df = pd.read_csv("results.csv")
        st.dataframe(df)
        
        visualization_type = st.selectbox("Choose Visualization", ("NONE", "PIE CHART", "HISTOGRAM", "SCATTER PLOT"))
        
        if visualization_type == "PIE CHART":
            sentiment_counts = df['Sentiment'].value_counts()
            fig = px.pie(values=sentiment_counts, names=sentiment_counts.index)
            st.plotly_chart(fig)
        
        elif visualization_type == "HISTOGRAM":
            column = st.selectbox("Choose column", df.columns)
            if column:
                fig = px.histogram(df, x=column, color='Sentiment')
                st.plotly_chart(fig)
        
        elif visualization_type == "SCATTER PLOT":
            x_col = st.text_input("Enter the continuous column name")
            if x_col and x_col in df.columns:
                fig = px.scatter(df, x=x_col, y='Sentiment')
                st.plotly_chart(fig)
            else:
                st.error(f"Column '{x_col}' not found in the data.")
    
    except FileNotFoundError:
        st.error("No results file found. Please run the analysis first.")
    except Exception as e:
        st.error(f"An error occurred while displaying results: {e}")

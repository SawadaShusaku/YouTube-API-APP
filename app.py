import streamlit as st
import googleapiclient.discovery
import pandas as pd
import plotly.express as px

def get_video_info(api_key, video_id):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()
    return response['items'][0]

def get_video_comments(api_key, video_id):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    
    comments = []
    next_page_token = None
    
    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'author': comment['authorDisplayName'],
                'message': comment['textDisplay'],
                'timestamp': comment['publishedAt']
            })
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return comments

st.title('YouTube Video Analyzer')

api_key = st.sidebar.text_input('Enter your YouTube API Key', type='password')
video_url = st.sidebar.text_input('Enter YouTube Video URL')

if api_key and video_url:
    video_id = video_url.split('v=')[1]
    
    # Get video info
    video_info = get_video_info(api_key, video_id)
    st.header(video_info['snippet']['title'])
    st.image(video_info['snippet']['thumbnails']['high']['url'])
    st.write(f"Views: {video_info['statistics']['viewCount']}")
    st.write(f"Likes: {video_info['statistics']['likeCount']}")
    
    # Get video comments
    comments = get_video_comments(api_key, video_id)
    
    if comments:
        # Display comments
        st.subheader('Video Comments')
        for comment in comments[:10]:  # Display first 10 comments
            st.write(f"{comment['author']}: {comment['message']}")
        
        # Create DataFrame for analysis
        df = pd.DataFrame(comments)
        
        # Message count by author
        st.subheader('Top Commenters')
        author_counts = df['author'].value_counts().head(10)
        fig = px.bar(x=author_counts.index, y=author_counts.values)
        fig.update_layout(xaxis_title='Author', yaxis_title='Comment Count')
        st.plotly_chart(fig)
        
        # Word cloud (you might need to install wordcloud package)
        # from wordcloud import WordCloud
        # text = ' '.join(df['message'])
        # wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        # st.image(wordcloud.to_array())
    else:
        st.write('No comments found for this video.')

else:
    st.write('Please enter your YouTube API Key and Video URL in the sidebar to start.')
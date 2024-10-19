import streamlit as st
import pandas as pd
import plotly.express as px
from googleapiclient.discovery import build
import re
from collections import Counter
from janome.tokenizer import Tokenizer
import html

# 定数定義
TOP_N = 10
KEYWORD_TOP_N = 20

def get_video_details(youtube, video_id):
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id
    )
    response = request.execute()
    return response['items'][0]

def get_channel_details(youtube, channel_id):
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()
    return response['items'][0]

def get_video_comments(youtube, video_id):
    comments = []
    next_page_token = None
    
    while True:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'author': comment['authorDisplayName'],
                'text': comment['textDisplay'],
                'likes': comment['likeCount'],
                'published_at': comment['publishedAt'],
                'reply_count': item['snippet']['totalReplyCount']
            })
            
            if 'replies' in item:
                for reply in item['replies']['comments']:
                    reply_snippet = reply['snippet']
                    comments.append({
                        'author': reply_snippet['authorDisplayName'],
                        'text': reply_snippet['textDisplay'],
                        'likes': reply_snippet['likeCount'],
                        'published_at': reply_snippet['publishedAt'],
                        'reply_count': 0
                    })
        
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return comments

def clean_text(text):
    # HTMLエンティティをデコード
    text = html.unescape(text)
    # HTMLタグを削除
    text = re.sub(r'<[^>]+>', '', text)
    # URLを削除
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # 特殊文字と数字を削除
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    # 複数の空白を1つの空白に置換
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# テキストの形態素解析などを行う
def extract_keywords(text, n=10):
    # テキストをクリーンアップ
    cleaned_text = clean_text(text)
    # Janomeのトークナイザーを初期化
    tokenizer = Tokenizer()
    # ストップワードを定義（既存のリストを使用）
    stop_words = set(['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる', 'も', 'する', 'から', 'な', 'こと', 'として', 'い', 'や', 'れる', 'など', 'なっ', 'ない', 'この', 'ため', 'その', 'あっ', 'よう', 'また', 'もの', 'という', 'あり', 'まで', 'られ', 'なる', 'へ', 'か', 'だ', 'これ', 'によって', 'により', 'おり', 'より', 'による', 'ず', 'なり', 'られる', 'において', 'ば', 'なかっ', 'なく', 'しかし', 'について', 'せ', 'だっ', 'その後', 'できる', 'それ', 'う', 'ので', 'なお', 'のみ', 'でき', 'き', 'つ', 'における', 'および', 'いう', 'さらに', 'でも', 'ら', 'たり', 'その他', 'に関する', 'たち', 'ます', 'ん', 'なら', 'に対して', '特に', 'せる', '及び', 'これら', 'とき', 'では', 'にて', 'ほか', 'ながら', 'うち', 'そして', 'とともに', 'ただし', 'かつて', 'それぞれ', 'または', 'お', 'ほど', 'ものの', 'に対する', 'ほとんど', 'と共に', 'といった', 'です', 'とも', 'ところ', 'ここ'])
    # 形態素解析を行い、名詞、動詞、形容詞のみを抽出
    words = []
    for token in tokenizer.tokenize(cleaned_text):
        if token.part_of_speech.split(',')[0] in ['名詞', '動詞', '形容詞']:
            word = token.base_form.lower()
            if word not in stop_words and len(word) > 1:
                words.append(word)

    # 単語の出現回数をカウント
    word_counts = Counter(words)
    # バイグラムの出現回数をカウント（同じ単語の繰り返しを除外）
    bigrams = [' '.join(pair) for pair in zip(words, words[1:]) if pair[0] != pair[1]]
    bigram_counts = Counter(bigrams)

    # 単語とバイグラムの出現回数を合わせる
    all_counts = word_counts + bigram_counts
    return all_counts.most_common(n)


# ###########################################################################################################


def main():
    """
    メイン関数：アプリケーションのエントリーポイント
    YouTubeの動画分析を実行し、結果を表示する
    """
    st.title('YouTube動画分析アプリ')

    # サイドバーでAPIキーと動画URLを入力
    api_key = st.sidebar.text_input('YouTube Data APIキーを入力', type='password')
    video_url = st.sidebar.text_input('YouTubeの動画URLを入力')

    if api_key and video_url:
        try:
            # YouTube API クライアントの初期化
            youtube = build('youtube', 'v3', developerKey=api_key)
            video_id = video_url.split('v=')[1]
            
            # 動画、チャンネル、コメントの情報を取得
            video_details = get_video_details(youtube, video_id)
            channel_details = get_channel_details(youtube, video_details['snippet']['channelId'])
            comments = get_video_comments(youtube, video_id)
            
            # 各種情報の表示と分析
            display_video_info(video_details)
            display_comments_list(comments)
            display_channel_info(channel_details)
            analyze_comments(comments)
            
        except Exception as e:
            # エラーハンドリング
            st.error(f"エラーが発生しました: {str(e)}")
            st.error("詳細なエラー情報:")
            st.exception(e)
    else:
        st.write('分析を開始するには、サイドバーにYouTube APIキーと動画URLを入力してください。')

def display_video_info(video_details):
    """
    動画の詳細情報を表示する
    
    :param video_details: 動画の詳細情報を含む辞書
    """
    st.header('動画情報')
    col1, col2 = st.columns(2)
    with col1:
        st.image(video_details['snippet']['thumbnails']['high']['url'])
    with col2:
        st.subheader(video_details['snippet']['title'])
        st.write(f"チャンネル: 　{video_details['snippet']['channelTitle']}")
        st.write(f"公開日: 　{video_details['snippet']['publishedAt']}")
        st.write(f"視聴回数: 　{video_details['statistics']['viewCount']}")
        st.write(f"高評価数: 　{video_details['statistics'].get('likeCount', 'N/A')}")
        st.write(f"コメント数: 　{video_details['statistics']['commentCount']}")
        st.write(f"説明: 　{video_details['snippet']['description'][:500]}...")


def display_comments_list(comments):
    """
    コメントの一覧を表示する
    
    :param comments: コメントのリスト
    :return: コメントのDataFrame
    """
    st.header('コメント一覧')
    df = pd.DataFrame(comments)
    df['published_at'] = pd.to_datetime(df['published_at'])
    st.dataframe(df[['author', 'text', 'likes', 'published_at']])
    return df

def display_channel_info(channel_details):
    """
    チャンネルの情報を表示する
    
    :param channel_details: チャンネルの詳細情報を含む辞書
    """
    st.header('チャンネル詳細情報')
    st.write(f"登録者数: {channel_details['statistics']['subscriberCount']}")
    st.write(f"総視聴回数: {channel_details['statistics']['viewCount']}")
    st.write(f"総動画数: {channel_details['statistics']['videoCount']}")

def analyze_comments(comments):
    """
    コメントの分析を行い、結果を表示する
    
    :param comments: コメントのリスト
    """
    df = pd.DataFrame(comments)
    df['published_at'] = pd.to_datetime(df['published_at'])

    st.header('コメント分析')
    
    display_basic_stats(df)
    display_comments_over_time(df)
    display_top_commenters(df)
    display_most_liked_comments(df)
    display_comment_length_distribution(df)
    display_most_replied_comments(df)
    display_keyword_analysis(df)

def display_basic_stats(df):
    """
    コメントの基本統計情報を表示する
    
    :param df: コメントのDataFrame
    """
    st.subheader('基本統計')
    st.write(f"総コメント数: {len(df)}")
    st.write(f"ユニークコメンター数: {df['author'].nunique()}")
    st.write(f"コメント平均高評価数: {df['likes'].mean():.2f}")

def display_comments_over_time(df):
    """
    時間経過によるコメント数の推移を表示する
    
    :param df: コメントのDataFrame
    """
    st.subheader('時間経過によるコメント数')
    df_daily = df.resample('D', on='published_at').size().reset_index(name='count')
    fig = px.line(df_daily, x='published_at', y='count')
    fig.update_layout(xaxis_title='日付', yaxis_title='コメント数')
    st.plotly_chart(fig)

def display_top_commenters(df):
    """
    トップコメンターを表示する
    
    :param df: コメントのDataFrame
    """
    st.subheader('トップコメンター')
    top_commenters = df['author'].value_counts().head(TOP_N)
    fig = px.bar(x=top_commenters.index, y=top_commenters.values)
    fig.update_layout(xaxis_title='コメンター', yaxis_title='コメント数')
    st.plotly_chart(fig)

def display_most_liked_comments(df):
    """
    最も高評価されたコメントを表示する
    
    :param df: コメントのDataFrame
    """
    st.subheader('最も高評価されたコメント')
    most_liked = df.nlargest(TOP_N, 'likes')
    st.table(most_liked[['author', 'text', 'likes']])

def display_comment_length_distribution(df):
    """
    コメント長の分布を表示する
    
    :param df: コメントのDataFrame
    """
    st.subheader('コメント長の分布')
    df['comment_length'] = df['text'].str.len()
    fig = px.histogram(df, x='comment_length', nbins=50)
    fig.update_layout(xaxis_title='コメント長', yaxis_title='頻度')
    st.plotly_chart(fig)

def display_most_replied_comments(df):
    """
    最も返信の多いコメントを表示する
    
    :param df: コメントのDataFrame
    """
    st.subheader('議論を呼んだコメント（リプライ数順）')
    most_replied = df.nlargest(TOP_N, 'reply_count')
    st.table(most_replied[['author', 'text', 'reply_count']])

def display_keyword_analysis(df):
    """
    頻出キーワードの分析結果を表示する
    
    :param df: コメントのDataFrame
    """
    
    st.subheader('頻出キーワード分析')
    all_keywords = []
    for text in df['text']:
        all_keywords.extend(extract_keywords(text))
    # キーワードの処理を修正
    processed_keywords = []
    for keyword, count in all_keywords:
        if isinstance(keyword, tuple):
            processed_keywords.append((' '.join(keyword), count))
        else:
            processed_keywords.append((keyword, count))
    
    keyword_counts = Counter(dict(processed_keywords)).most_common(KEYWORD_TOP_N)
    keyword_df = pd.DataFrame(keyword_counts, columns=['Keyword', 'Count'])

    # 横棒グラフの作成
    fig = px.bar(keyword_df, x='Count', y='Keyword', orientation='h', 
                text='Count', height=600)
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, 
                    title=f'頻出キーワード（上位{KEYWORD_TOP_N}件）',
                    xaxis_title='出現回数',
                    yaxis_title='')
    st.plotly_chart(fig)
    # テーブル形式でも表示
    st.subheader('頻出キーワード詳細')
    st.table(keyword_df)

if __name__ == "__main__":
    main()
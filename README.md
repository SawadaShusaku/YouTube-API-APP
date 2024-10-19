# YouTube動画分析アプリ / YouTube Video Analysis App

## 概要 / Overview

このアプリケーションは、YouTube動画の詳細情報、コメント、チャンネル情報を分析し、視覚化するStreamlitベースのWebアプリケーションです。

This is a Streamlit-based web application that analyzes and visualizes detailed information, comments, and channel information of YouTube videos.

## 機能 / Features

- 動画の基本情報表示（タイトル、サムネイル、視聴回数など）
- チャンネル情報の表示
- コメントの一覧表示と分析
  - 時間経過によるコメント数の推移
  - トップコメンター
  - 最も高評価されたコメント
  - コメント長の分布
  - 最も返信の多いコメント
  - 頻出キーワード分析

- Display basic video information (title, thumbnail, view count, etc.)
- Display channel information
- List and analyze comments
  - Comment count over time
  - Top commenters
  - Most liked comments
  - Comment length distribution
  - Most replied comments
  - Frequent keyword analysis

## 必要条件 / Requirements

- Python 3.6以上
- YouTube Data API v3のAPIキー

- Python 3.6 or higher
- YouTube Data API v3 API key

## インストール / Installation

1. リポジトリをクローンします：
   Clone the repository:
   ```
   git clone https://github.com/yourusername/youtube-analysis-app.git
   cd youtube-analysis-app
   ```

2. 必要なパッケージをインストールします：
   Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## 使用方法 / Usage

1. Streamlitアプリを実行します：
   Run the Streamlit app:
   ```
   streamlit run youtube_video_analyzer.py
   ```

2. ブラウザでアプリが開きます。
   The app will open in your browser.

3. サイドバーにYouTube Data APIキーと分析したい動画のURLを入力します。
   Enter your YouTube Data API key and the URL of the video you want to analyze in the sidebar.

4. アプリが自動的に分析を開始し、結果を表示します。
   The app will automatically start the analysis and display the results.

## 依存ライブラリ / Dependencies

- streamlit
- pandas
- plotly
- google-api-python-client
- janome

## 注意事項 / Notes

- YouTube Data APIの利用制限に注意してください。
- APIキーは安全に管理し、公開リポジトリにコミットしないよう注意してください。

- Be aware of the usage limits of the YouTube Data API.
- Manage your API key securely and be careful not to commit it to public repositories.

## ライセンス / License

このプロジェクトは[MITライセンス](https://opensource.org/licenses/MIT)の下で公開されています。

This project is released under the [MIT License](https://opensource.org/licenses/MIT).

## 貢献 / Contributing

バグ報告や機能リクエストは、GitHubのIssueを通じてお願いします。プルリクエストも歓迎です。

Bug reports and feature requests are welcome through GitHub Issues. Pull requests are also welcome.

## 作者 / Author

[Sawada]


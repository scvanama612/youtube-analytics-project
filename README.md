YouTube Analytics Project
This project is an end-to-end pipeline I built to collect, store, and analyze YouTube channel performance data. The goal was to create a real-world example of how data engineering and data analysis can be combined to generate meaningful insights for a content creator.
I designed this system so that it can automatically extract channel and video data using the YouTube Data API, save it into a structured database, and then run analysis to understand what type of content performs well.
Project Overview
The project focuses on four main areas:
•	Collecting raw data from the YouTube Data API
•	Transforming and organizing the data into clean tables
•	Storing the results inside a SQLite database
•	Analyzing the data inside a Jupyter Notebook to produce insights
•	This workflow shows how to move from API data extraction all the way to analysis in a reproducible and automated way.
What the Pipeline Does
Data Collection
The script gathers the following information from a YouTube channel:
•	Channel name, ID, subscribers, total views, and video count
•	All video metadata (title, description, publish date, duration, tags, category)
•	Daily snapshot values such as views, likes, and comments
Database
A SQLite database called youtube_analytics.db stores three tables:
•	channels
•	videos
•	video_stats
The structure allows multiple snapshots over time so performance trends can be tracked.
Analysis
The notebook includes several basic analyses such as:
•	Top performing videos
•	Engagement comparison between videos
•	How publish dates relate to performance
•	Categorizing content types
•	General channel growth observations
This helps a creator understand which videos work well and what type of content viewers prefer.
Technologies Used
Python
YouTube Data API
SQLite
SQLAlchemy
Pandas
Jupyter Notebook
Purpose of the Project
The main purpose of this project is to build a complete data pipeline that collects and analyzes YouTube channel data in an organized way. I wanted to take a real platform like YouTube and create a system that automatically pulls channel and video information, stores it cleanly in a database, and generates insights that a creator can actually use. This allowed me to practice real data engineering steps such as API integration, data extraction, transformation, and database design.
Another reason for developing this project was to use my data science skills on a real-life scenario instead of using common datasets. I wanted a project that felt practical, realistic, and valuable. This system helped me understand how to take raw API responses and convert them into structured tables that can be analyzed easily. It also helped me work on ETL logic, SQL operations, and building reusable scripts.
I built this project specifically for a YouTube creator I know. They wanted to understand which of their videos perform well and what type of content brings the most engagement. The project helps answer questions like which videos viewers watch the most, which topics get the best response, and how the channel is growing over time. It gives them clearer insights than the default YouTube dashboard and helps them plan future content.
Through this project, I also developed the entire analysis environment using pandas and Jupyter Notebook. The analysis shows top videos, engagement patterns, performance trends, and comparisons between different videos. The goal was to make the data easy to explore and interpret so the creator can improve their channel strategy. Overall, the project shows how data can be used to support content decisions and increase channel performance.



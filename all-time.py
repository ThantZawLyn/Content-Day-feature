import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer                             
import pyidaungsu as pds
from numpy.linalg import norm
from time import sleep
import pickle
import warnings
import emoji
import re
import time
import enum
from sklearn.metrics.pairwise import cosine_similarity
warnings.filterwarnings('ignore')
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import VARCHAR, Boolean, Column, DateTime, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import BYTEA, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy import update, and_
import os
from load_featrue import load_feature
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # hide warning
# from ..constants import SQLALCHEMY_DATABASE_URI

#engine = create_engine(SQLALCHEMY_DATABASE_URI)
engine = create_engine('postgresql://fbs:yah7WUy1Oi8G@172.32.253.129:5432/fbs', echo=False)

Base = declarative_base(bind=engine)
session_creator = sessionmaker()
DBSession = session_creator()
warnings.filterwarnings('ignore')

class LikeType(enum.Enum):
    like = "like"
    love = "love"
    haha = "haha"
    wow = "wow"
    sad = "sad"
    angry = "angry"

class TaskType(str, enum.Enum):
    keyword: str = "keyword"
    source: str = "source"
    like: str = "like"
    comment: str = "comment"
    share: str = "share"
    personal_page: str = "personal_page"

class SubtaskType(str, enum.Enum):
    like: str = "like"
    comment: str = "comment"
    share: str = "share"
    personal_page: str = "personal_page"

class TaskStatus(str, enum.Enum):
    in_queue: str = "in_queue"
    in_progress: str = "in_progress"
    success: str = "success"
    retry: str = "retry"
    failed: str = "failed"

class Subtask(Base):
    __tablename__ = 'subtasks'
    id = Column('id', Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="subtasks", uselist=False)

    subtask_type = Column(ENUM(SubtaskType))

    start_time = Column('start_time', DateTime)
    end_time = Column('end_time', DateTime)

    status = Column(ENUM(TaskStatus))

class SubtaskPersonalData(Base):
    __tablename__ = 'subtask_personal_data'
    id = Column('id', Integer, primary_key=True)
    subtask_id = Column(Integer, ForeignKey('subtasks.id'))
    subtask = relationship("Subtask")

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")

class Post(Base):
    __tablename__ = 'posts'

    def __hash__(self):
        return hash(self.fb_post_id)

    def __eq__(self, other):
        return isinstance(other, Post) and self.fb_post_id == other.fb_post_id

    id = Column('id', Integer, primary_key=True)
    date = Column('date', DateTime)
    last_time_updated = Column('last_time_updated', DateTime)
    fb_post_id = Column('fb_post_id', VARCHAR(1024))
    fb_repost_id = Column('fb_repost_id', VARCHAR(128))
    fb_repost_link = Column('fb_repost_link', VARCHAR(2048))
    fb_post_link = Column('fb_post_link', VARCHAR(1024))
    fb_post_link_likes = Column('fb_post_link_likes', VARCHAR(1024))
    content_id = Column(Integer, ForeignKey('content.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    stat_id = Column(Integer, ForeignKey('post_stat.id'))

    content = relationship("Content", back_populates="post", uselist=False)
    likes = relationship("Like", back_populates="post")
    comments = relationship("Comment", back_populates="post")
    shares = relationship("Share", back_populates="post")
    user = relationship("User", back_populates="post", uselist=False)
    task = relationship("Task", back_populates="post", uselist=False)
    stat = relationship("PostStat", back_populates="post", uselist=False)
    subtasks = relationship("Subtask", back_populates="post", uselist=True)

class PostStat(Base):
    __tablename__ = 'post_stat'
    id = Column('id', Integer, primary_key=True)
    likes = Column('likes', VARCHAR(32))
    comments = Column('comments', VARCHAR(32))
    shares = Column('shares', VARCHAR(32))

    post = relationship("Post", back_populates="stat", uselist=False)

    def is_equals(self, post_stat):
        return self.likes == post_stat.likes and self.comments == post_stat.comments and self.shares == post_stat.shares

class Content(Base):
    __tablename__ = 'content'
    id = Column('id', Integer, primary_key=True)
    text = Column('text', VARCHAR(1024))
    nlp_id = Column(Integer, ForeignKey('nlp.id'),  nullable=True)

    post = relationship("Post", back_populates="content", uselist=False)
    comment = relationship("Comment", back_populates="content", uselist=False)
    photos = relationship("Photo", back_populates="content", uselist=True)
    videos = relationship("Video", back_populates="content", uselist=True)

class NLP(Base):
    __tablename__ = 'nlp'
    id = Column('id', Integer, primary_key=True)
    Category = Column('category', VARCHAR(255))
    
class Photo(Base):
    __tablename__ = 'photos'
    id = Column('id', Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('content.id'))
    photo_link = Column('photo_link', VARCHAR(1024))

    content = relationship("Content", back_populates="photos")

class Video(Base):
    __tablename__ = 'videos'
    id = Column('id', Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('content.id'))
    video_link = Column('video_link', VARCHAR(1024))

    content = relationship("Content", back_populates="videos")

class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True)

    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="likes")

    comment_id = Column(Integer, ForeignKey('comments.id'))
    comment = relationship("Comment", back_populates="likes")

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="likes")

    like_type = Column(ENUM(LikeType))

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)

    date = Column(DateTime)
    fb_comment_id = Column('fb_comment_id', VARCHAR(255))

    content_id = Column(Integer, ForeignKey('content.id'))
    content = relationship("Content", back_populates="comment")

    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="comments")

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="comments")

    parent_comment_id = Column(Integer, ForeignKey('comments.id'))
    parent_comment = relationship("Comment", back_populates="child_comments", remote_side=[id])
    child_comments = relationship("Comment", back_populates="parent_comment", remote_side=[parent_comment_id])

    likes = relationship("Like", back_populates="comment")
    likes_count = Column('likes_count', Integer)

class Share(Base):
    __tablename__ = 'shares'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="shares")

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="shares")

class UserUniversity(Base):
    __tablename__ = 'user_university'
    id = Column(Integer, primary_key=True)
    name = Column('name', VARCHAR(1024))
    info = Column('info', VARCHAR(1024))
    link = Column('link', VARCHAR(1024))

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="universities")

class UserJob(Base):
    __tablename__ = 'user_job'
    id = Column(Integer, primary_key=True)
    name = Column('name', VARCHAR(1024))
    info = Column('info', VARCHAR(1024))
    link = Column('link', VARCHAR(1024))

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="jobs")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)

    name = Column("name", VARCHAR(1024))
    link = Column("link", VARCHAR(1024))
    sex = Column("sex", VARCHAR(8))
    city_of_birth = Column("city_of_birth", VARCHAR(128))
    current_city = Column("current_city", VARCHAR(128))
    birthday = Column("birthday", VARCHAR(128))
    fb_id = Column("fb_id", VARCHAR(32))
    check = Column("check",Boolean)
    
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    shares = relationship("Share", back_populates="user")
    post = relationship("Post", back_populates="user")

    universities = relationship("UserUniversity", back_populates="user")
    jobs = relationship("UserJob", back_populates="user")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column('id', Integer, primary_key=True)
    interval = Column('interval', Integer)
    retro = Column('retro', DateTime)
    until = Column('until', DateTime)
    received_time = Column('received_time', DateTime)
    finish_time = Column('finish_time', DateTime)
    status = Column(ENUM(TaskStatus))
    enabled = Column('enabled', Boolean)
    post = relationship("Post", back_populates="task")

class TaskKeyword(Base):
    __tablename__ = 'tasks_keyword'
    id = Column('id', Integer, primary_key=True)
    keyword = Column('keyword', VARCHAR(255))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship("Task")

class TaskSource(Base):
    __tablename__ = 'tasks_source'
    id = Column('id', Integer, primary_key=True)
    source_id = Column('source_id', VARCHAR(255))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship("Task")

class WorkerCredential(Base):
    __tablename__ = 'worker_credentials'
    id = Column('id', Integer, primary_key=True)
    inProgress = Column('inProgress', Boolean)
    inProgressTimeStamp = Column('in_progress_timestamp', DateTime)
    last_time_finished = Column('last_time_finished', DateTime)
    locked = Column('locked', Boolean)
    alive_timestamp = Column('alive_timestamp', DateTime)

    account_id = Column(Integer, ForeignKey('accounts.id'))
    proxy_id = Column('proxy_id', ForeignKey('proxy.id'))
    user_agent_id = Column('user_agent_id', ForeignKey('user_agent.id'))

    account = relationship("FBAccount", uselist=False)
    proxy = relationship("Proxy", uselist=False)
    user_agent = relationship("UserAgent", uselist=False)

class WorkingCredentialsTasks(Base):
    __tablename__ = 'worker_credentials_tasks'
    id = Column('id', Integer, primary_key=True)
    worker_credentials_id = Column(Integer, ForeignKey('worker_credentials.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    type = Column('type', VARCHAR(16))
    start_timestamp = Column('start_timestamp', DateTime)
    finish_timestamp = Column('finish_timestamp', DateTime)

class Proxy(Base):
    __tablename__ = 'proxy'
    id = Column('id', Integer, primary_key=True)
    host = Column('host', VARCHAR(255))
    port = Column('port', Integer)
    login = Column('login', VARCHAR(255))
    password = Column('password', VARCHAR(255))
    available = Column('available', Boolean)
    last_time_checked = Column('last_time_checked', DateTime)
    attempts = Column('attempts', Integer)

class FBAccount(Base):
    __tablename__ = 'accounts'
    id = Column('id', Integer, primary_key=True)
    login = Column('login', VARCHAR(255))
    password = Column('password', VARCHAR(255))
    available = Column('available', Boolean, nullable=False)
    cookies = relationship("Cookies", uselist=False)
    availability_check = Column('availability_check', DateTime)

class Cookies(Base):
    __tablename__ = 'cookies'
    id = Column('id', Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    row_data = Column('row_data', BYTEA)

class UserAgent(Base):
    __tablename__ = 'user_agent'
    id = Column('id', Integer, primary_key=True)
    userAgentData = Column('userAgentData', VARCHAR(2048))
    window_size_id = Column(Integer, ForeignKey('window_size.id'))
    window_size = relationship("WindowSize")

class WindowSize(Base):
    __tablename__ = 'window_size'
    id = Column('id', Integer, primary_key=True)
    width = Column('width', Integer)
    height = Column('height', Integer)



class All_content(Base):
    __tablename__ = 'all_content'
    id = Column(Integer, primary_key=True)
    content_id = Column("content_id", Integer)
    network_id = Column("network_id", Integer)
    nlp_id = Column('nlp_id', Integer)
    ht_check = Column('ht_check', VARCHAR(32))
    keyword_check = Column('keyword_check', VARCHAR(32))
    check_similarity = Column('check_similarity', VARCHAR(32))

class Yt(Base):
    __tablename__ = 'youtube_channel'
    id = Column(Integer, primary_key=True)
    channel_id = Column("channel_id", VARCHAR(32))
    channel_name = Column("channel_name", VARCHAR(32))
    playlist_id= Column("playlist_id", VARCHAR(32))
    active= Column("active", VARCHAR(32))
    youtube_st = relationship("Yt_st", back_populates="youtube_ch")
    youtube_vdo = relationship("Yt_vd", back_populates="youtube_vdo")

class Yt_st(Base):
    __tablename__ = 'youtube_st'
    id = Column(Integer, primary_key=True)
    subscribers= Column("subscribers", Integer)
    views= Column("views", Integer)
    videos= Column("videos", Integer)
    date= Column('date', DateTime)
    youtube_channel_id = Column(Integer, ForeignKey('youtube_channel.id'))
    youtube_ch = relationship("Yt", back_populates="youtube_st")

class Yt_vd(Base):
    __tablename__ = 'youtube_vd'
    id = Column(Integer, primary_key=True)
    video_id = Column("video_id",  VARCHAR(32))
    youtube_channel_id = Column(Integer, ForeignKey('youtube_channel.id'))
    youtube_vdo = relationship("Yt", back_populates="youtube_vdo")
    nlp_id = Column(Integer, ForeignKey('nlp.id'), nullable=True)
    title =Column("title",  VARCHAR(1024))
    description = Column("description",  VARCHAR(16348))
    tags = Column("tags",  VARCHAR(1024))
    date = Column('date', DateTime)
    viewcount = Column("viewcount", Integer)
    likecount = Column("likecount", Integer)
    commentcount = Column("commentcount", Integer)
    definition = Column("definition",  VARCHAR(32))
    caption = Column("caption",  VARCHAR(32))
    durationsecs = Column("durationsecs", Integer)
    tagcount = Column("tagcount", Integer)

class Tg(Base):
    __tablename__ = 'tele_content'
    id = Column(Integer, primary_key=True)
    username = Column("username", VARCHAR(1024))
    channel_id = Column("channel_id", Integer)
    msg_id = Column('msg_id', Integer)
    #nlp_id = Column(Integer, ForeignKey('nlp.id'),  nullable=True)
    text = Column('text', VARCHAR(16384)) 
    #message = Column('message', VARCHAR CHECK(length(message) <=500)
    date = Column('date', DateTime)
    #date = Column('date', VARCHAR(1024))
    signature = Column("signature", VARCHAR(1024))
    msg_link = Column('msg_link', VARCHAR(1024))
    views = Column('views', VARCHAR(32))
    number_replies = Column('number_replies', VARCHAR(32))
    number_forwards  = Column('number_forwards', VARCHAR(32))
    is_forward =  Column('is_forward', VARCHAR(32))
    forward_msg_date = Column('forward_msg_date', DateTime)
    forward_msg_date_string =Column('forward_msg_date_string', VARCHAR(32))
    forward_msg_link = Column('forward_msg_link', VARCHAR(1024))
    from_channel_id = Column("from_channel_id", Integer)
    from_channel_name = Column("from_channel_name", VARCHAR(1024))
    is_reply =  Column("is_reply", VARCHAR(32))
    reply_to_msg_id = Column("reply_to_msg_id", VARCHAR(32))
    reply_msg_link = Column('reply_msg_link', VARCHAR(1024))
    contains_media  = Column('contains_media', VARCHAR(32))
    media_type = Column('media_type', VARCHAR(1024))
  

class Tg_channel(Base):
    __tablename__ = 'tele_channel'
    id = Column(Integer, primary_key=True)
    username = Column("username", VARCHAR(1024))
    channel_id = Column("channel_id", VARCHAR(32))
    max_id = Column('max_id', Integer)
    craw_id = Column('craw_id', Integer)

class Tw(Base):
    __tablename__ = 'twitter_channel'
    id = Column(Integer, primary_key=True)
    user_name = Column("user_name", VARCHAR(32))
    active = Column("active", VARCHAR(32))
    display_name = Column("display_name", VARCHAR(32))

class Tw_vd(Base):
    __tablename__ = 'twitter_content'
    id = Column(Integer, primary_key=True)
    date = Column("date", DateTime)
    user_name = Column("user_name",  VARCHAR(255))
    tweet_id = Column("tweet_id",  VARCHAR(255))
    nlp_id = Column(Integer, ForeignKey('nlp.id'), nullable=True)
    text = Column("text",  VARCHAR(16348))
    language = Column("language",  VARCHAR(1024))
    hashtags = Column("hashtags", VARCHAR(1024))
    reply_count = Column("reply_count", Integer)
    retweet_count = Column("retweet_count", Integer)
    like_count = Column("like_count", Integer)
    view_count = Column("view_count", Integer)
    quote_count = Column("quote_count", Integer)
    url = Column("url", VARCHAR(1024))

class Topic_modeling(Base):
    __tablename__ = 'topic_modeling'
    id = Column(Integer, primary_key=True)
    content_id = Column("content_id", Integer)
    network_id = Column("network_id", Integer)
    upload_date = Column("upload_date", DateTime)
    run_date = Column("run_date", DateTime)
    clusters = Column("clusters", Integer)
    top_terms = Column("top_terms", VARCHAR(1024))

class Top_keyword(Base):
    __tablename__ = 'top_keyword'
    id = Column(Integer, primary_key=True)
    keyword = Column("keyword", VARCHAR(1024))
    count = Column("count", Integer)
    run_date = Column("run_date", DateTime)

class Content_similarity(Base):
    __tablename__ = 'content_similarity'
    id = Column(Integer, primary_key=True)
    content_id = Column('content_id', Integer)
    network_id = Column('network_id', Integer)
    similar_content_id = Column('similar_content_id', Integer)
    similar_network_id = Column('similar_network_id', Integer)
    similarity_value = Column('similarity_value', Float)


similarity_value = 0.60  # set similarity_value

def tokenize(line):
    sentence = pds.tokenize(line,form="word")
    return sentence

#Load_Data
t1 = time.perf_counter()
print("Loadiing monthly data...")

folder_path = "./data_3000/"
# List all files in the folder
files = os.listdir(folder_path)
# Filter out only CSV files and strip the extension
file_names = [os.path.splitext(file)[0] for file in files if file.endswith('.csv')]
# Print the list of CSV file names without the extension
print(file_names)

data_dict = {}
feature_dict = {}
vectorizer_dict = {}

for file_name in file_names:
    csv_file = f"./data_3000/{file_name}.csv"
    pickle_file = f"./data_3000/{file_name}.pickle"
    vectorizer_file = f"./data_3000/{file_name}_vectorizer.pickle"

    data, feature, vectorizer = load_feature(csv_file, pickle_file, vectorizer_file)

    # Create variables dynamically
    data_dict[f"data_{file_name}"] = data
    feature_dict[f"feature_{file_name}"] = feature
    vectorizer_dict[f"vectorizer_{file_name}"] = vectorizer

t2 = time.perf_counter()
print(f'Loaded monthly data: {t2 - t1} seconds')

# Data_Cleaning
stopwordslist = []
slist = []
with open("stopword.txt", encoding = 'utf8') as stopwordsfile:
    stopwords = stopwordsfile.readlines()
    slist.extend(stopwords)
    for w in range(len(slist)):
        temp = slist[w]
        stopwordslist.append(temp.rstrip())
CleanPattern = re.compile(r'\d+|[·’■‘_၊။“”+#…!-/:-@[-`.{-~\t]|[A-za-z0-9]')
def clean_sentence(sentence):
     sentence = sentence.replace("_"," ")
     sent = CleanPattern.sub(" ",sentence)
     return sent

def remove_emoji(sentence):
    new_text=emoji.demojize(sentence)
    return new_text

def stop_word(sentence):
  new_sentence = []
  for word in sentence.split():
    if word not in stopwordslist:
      new_sentence.append(word)
  return(' '.join(new_sentence))

def tokenize(line):
    line= remove_emoji(line)
    line = clean_sentence(line)
    sentence = pds.tokenize(line,form="word")
    sentence = ' '.join([str(elem) for elem in sentence])
    sentence = stop_word(sentence)
    return sentence

# Check similarity function
def check(text, vectorizer, feature, data):
    results_df = pd.DataFrame(columns=['Cosine Similarity','Content_ID','Network_ID', 'Description', 'Upload_Date',])
    text = vectorizer.transform([text]).toarray()
    temp = feature.shape[0]
    for i in range(temp):
        # define two lists or array
        A= np.squeeze(np.asarray(feature[i]))
        B = np.squeeze(np.asarray(text))
        cosine = np.dot(A,B)/(norm(A)*norm(B))
        #print(i)
        if cosine>=similarity_value:
            #print( i)
            results_df = results_df.append({
                    'Cosine Similarity': cosine,
                    'Content_ID': data['Content_ID'].iloc[i],
                    'Network_ID': data['Network_ID'].iloc[i],
                    'Description': data['Description'].iloc[i],  # Include the description
                    'Upload_Date': data['Upload_Date'].iloc[i],
                }, ignore_index=True)   
    return(results_df)

with open("remove.txt", "r", encoding="utf-8") as file:
    text_to_remove = [line.strip() for line in file.readlines()]

while True:
    records_found = False
    # Retrieved Content from All_Content
    a=(DBSession.query(All_content.id , All_content.content_id, All_content.network_id)
        .filter(All_content.id > 1849380)
        .filter(All_content.check_similarity == None)
        .order_by(All_content.id.desc()).limit(1))

    for row in a:
        records_found = True
        Content_id =row.content_id
        Network_id=row.network_id
        ID = row.id

        # Processing status 
        stmt = (update(All_content).where(All_content.id == ID).values(check_similarity='processing'))
        DBSession.execute(stmt, execution_options={"synchronize_session": False})
        DBSession.commit() 

        # ID
        print("\033[33mAll_content ID : \033[0m" + f"\033[33m{str(ID)}\033[0m") 

        # for facebook
        if (Network_id==1): 
            try:
                text = DBSession.query(Content.text,Content.id).filter(Content.id == Content_id).first()
                id = text[1]
                print("\033[34mFacebook ID : \033[0m" + f"\033[34m{str(id)}\033[0m")
                print(text[0])
                sentence = text[0].replace("\n", " ")
            except Exception as e:
                print(KeyError)

            # Find the index of the start and end of the specified section
            found_keywords = [keyword for keyword in text_to_remove if keyword in sentence]
            # Remove found keywords from the sentence
            for keyword in found_keywords:
                sentence = sentence.replace(keyword, '')
            text = tokenize(sentence)
            
            #print(text)
            
        ## for YouTube
        if (Network_id==2): 
            #print("YouTube")
            text = DBSession.query(Yt_vd.description,Yt_vd.id).filter(Yt_vd.id == Content_id).first()
            id = text[1]
            print("\033[31mYoutube ID : \033[0m" + f"\033[31m{str(id)}\033[0m")
            print(text[0])
            sentence = text[0].replace("\n", " ")

            # Find the index of the start and end of the specified section
            found_keywords = [keyword for keyword in text_to_remove if keyword in sentence]
            # Remove found keywords from the sentence
            for keyword in found_keywords:
                sentence = sentence.replace(keyword, '')
            text = tokenize(sentence)
        
        ## for Telegram
        elif (Network_id==3):
            #print("Telegram")
            text = DBSession.query(Tg.text,Tg.id).filter(Tg.id == Content_id).first()
            id = text[1]
            print("\033[36mTelegram ID : \033[0m" + f"\033[34m{str(id)}\033[0m")
            sentence = text[0].replace("\n", " ")
            print(text[0])

           # Find the index of the start and end of the specified section
            found_keywords = [keyword for keyword in text_to_remove if keyword in sentence]
            # Remove found keywords from the sentence
            for keyword in found_keywords:
                sentence = sentence.replace(keyword, '')
            text = tokenize(sentence)
            #print(text)

        ## for twitter
        elif (Network_id==4):
            #print("Twitter")
            text = DBSession.query(Tw_vd.text,Tw_vd.id).filter(Tw_vd.id == Content_id).first()
            id = text[1]
            print("\033[36mTwitter ID : \033[0m" + f"\033[34m{str(id)}\033[0m")
            print(text[0])
            sentence = text[0].replace("\n", " ")

            # Find the index of the start and end of the specified section
            found_keywords = [keyword for keyword in text_to_remove if keyword in sentence]
            # Remove found keywords from the sentence
            for keyword in found_keywords:
                sentence = sentence.replace(keyword, '')
            text = tokenize(sentence)
            #print(text)

        # Load Day Content
        data_today, feature_today, vectorizer_today = load_feature(
            "./data_today/today.csv",
            "./data_today/today.pickle",
            "./data_today/today_vectorizer.pickle"
                )
        print("Loaded today data")

        t1 = time.perf_counter()
        # Check Similarity 
        print("Checking similarity...")

        all_month_results_df = pd.DataFrame()
        # Check Today
        results_df_today   = check(text,vectorizer_today,feature_today,data_today) 
        # Check All Month
        for file_name in file_names:
            month_results_df = check(text,vectorizer_dict[f"vectorizer_{file_name}"],feature_dict[f"feature_{file_name}"] ,data_dict[f"data_{file_name}"])
            # Concatenate month results to the all_month_results_df DataFrame
            all_month_results_df = pd.concat([all_month_results_df, month_results_df], ignore_index=True)

        combined_results_df = pd.concat([results_df_today , all_month_results_df], ignore_index=True) 

        t2 = time.perf_counter()
        print(f'Check Time: {t2 - t1} seconds')
        
        print("Number of Similar Contents :" +str(len(combined_results_df)))
        
        # Save to Database
        print("Saving to Database...")
        for i in range(len(combined_results_df)):
            Cosine_Similarity = combined_results_df['Cosine Similarity'].iloc[i]
            Similar_Content_ID = combined_results_df['Content_ID'].iloc[i]
            Similar_Network_ID = combined_results_df['Network_ID'].iloc[i]

            same_id = DBSession.query(Content_similarity.id).filter(
                            and_(
                            Content_similarity.content_id == id,
                            Content_similarity.network_id == Network_id,
                            Content_similarity.similar_content_id == Similar_Content_ID,
                            Content_similarity.similar_network_id == Similar_Network_ID
                                            )
                                                                    ).first()
            if same_id:
                print("Data already exists")

            elif id == Similar_Content_ID and Network_id == Similar_Network_ID:
                print("Same content")

            else:

                add_todatabase= Content_similarity(content_id = id, 
                                                network_id = Network_id,
                                                similar_content_id = Similar_Content_ID,
                                                similar_network_id = Similar_Network_ID,
                                                similarity_value = Cosine_Similarity ) # add to database
                DBSession.add(add_todatabase)
                DBSession.commit() 
        
        # Finished status
        stmt = (update(All_content).where(All_content.id == ID).values(check_similarity='finished'))
        DBSession.execute(stmt, execution_options={"synchronize_session": False})
        DBSession.commit() 

        # combined_results_df.to_csv('similarity.csv', index=False)
        print("Finisihed Process")
        # Delelet all datat from result dataframe
        combined_results_df = pd.DataFrame(columns=[], index=[])
        results_df_today = pd.DataFrame(columns=[], index=[])
        all_month_results_df = pd.DataFrame(columns=[], index=[])

    if not records_found:
        print("No records found")
        #empty_attempts += 1
        sleep(30)
        # if empty_attempts >= max_empty_attempts:
        #     print("Max attempts reached without finding records. Exiting.")
        #     break
    


from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
import datetime
from database import Base

class ArticleStatus(enum.Enum):
    PENDING = "pending"         # Waiting to be generated
    GENERATED = "generated"     # AI has written it, waiting for humanization/review
    PUBLISHED = "published"     # Pushed to WordPress
    FAILED = "failed"           # Error during generation/publishing

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True) # e.g., AI ToolKit Hub
    domain = Column(String(255), unique=True)
    
    clusters = relationship("Cluster", back_populates="site")

class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    topic_name = Column(String(255)) # e.g., AI Tools for Marketing
    
    site = relationship("Site", back_populates="clusters")
    articles = relationship("Article", back_populates="cluster")

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"))
    
    target_keyword = Column(String(255), index=True)
    title = Column(String(255))
    meta_description = Column(String(255))

    source_url = Column(String(500), nullable=True, unique=True)
    raw_content = Column(Text, nullable=True) # This will hold the YouTube transcript
    
    # Store the raw generated HTML/Text here before pushing to WP
    raw_content = Column(Text) 
    
    status = Column(Enum(ArticleStatus), default=ArticleStatus.PENDING)
    wp_post_id = Column(Integer, nullable=True) # To track the ID once it hits WordPress
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    published_at = Column(DateTime, nullable=True)

    cluster = relationship("Cluster", back_populates="articles")
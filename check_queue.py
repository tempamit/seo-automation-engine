from database import SessionLocal
from models import Article, ArticleStatus, Cluster, Site

def view_queue():
    db = SessionLocal()
    try:
        pending_articles = db.query(Article).filter(Article.status == ArticleStatus.PENDING).all()
        
        print(f"📊 TOTAL PENDING ARTICLES: {len(pending_articles)}\n")
        print("-" * 50)
        
        for index, article in enumerate(pending_articles, 1):
            cluster = db.query(Cluster).filter(Cluster.id == article.cluster_id).first()
            site = db.query(Site).filter(Site.id == cluster.site_id).first()
            
            print(f"{index}. [{site.name}] - {article.target_keyword}")
            
        print("-" * 50)
    finally:
        db.close()

if __name__ == "__main__":
    view_queue()
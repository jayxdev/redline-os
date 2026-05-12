import os
import re
import uuid
from datetime import datetime
from providers.mongo.client import MongoManager
from models.idea import Idea
from models.video import Video, VideoPlan, PostPackage, VideoMetrics

def parse_ideas(content):
    ideas = []
    # Split by Idea blocks
    blocks = re.split(r'### Idea \d+', content)
    for block in blocks[1:]: # Skip the header
        lines = block.strip().split('\n')
        idea_dict = {}
        for line in lines:
            if ':' in line:
                key, val = line.strip('- ').split(':', 1)
                idea_dict[key.strip()] = val.strip()
        
        if 'title' in idea_dict:
            tags = [t.strip() for t in idea_dict.get('pattern_tags', '').split(',')] if idea_dict.get('pattern_tags') else []
            ideas.append(Idea(
                idea_id=f"idea-{datetime.now().strftime('%Y-%m-%d')}-{len(ideas)}",
                title=idea_dict['title'],
                summary=idea_dict.get('concept', ''),
                angle=idea_dict.get('visual sequence', ''),
                rationale=idea_dict.get('why_it_should_work', ''),
                status='new',
                tags=tags
            ))
    return ideas

def parse_video(content):
    # Very basic parsing based on the template
    video_dict = {}
    
    # Extraction via regex
    video_id_match = re.search(r'- Video ID: (.*)', content)
    status_match = re.search(r'- Status: (.*)', content)
    hook_match = re.search(r'- Hook: (.*)', content)
    topic_match = re.search(r'- Topic: (.*)', content)
    caption_match = re.search(r'- Caption: (.*)', content)
    hashtags_match = re.search(r'- Hashtags used: (.*)', content)
    
    video_id = video_id_match.group(1).strip() if video_id_match else "unknown"
    status = status_match.group(1).strip() if status_match else "planned"
    
    plan = VideoPlan(
        hook=hook_match.group(1).strip() if hook_match else "",
        concept=topic_match.group(1).strip() if topic_match else "",
        beats=[],
        cta="",
        production_notes=[]
    )
    
    hashtags = [h.strip() for h in hashtags_match.group(1).split('#') if h.strip()] if hashtags_match else []
    
    package = PostPackage(
        selected_caption=caption_match.group(1).strip() if caption_match else None,
        hashtags=hashtags
    )
    
    return Video(
        video_id=video_id,
        title=video_id, # Fallback title
        status=status,
        plan=plan,
        post_package=package
    )

def migrate():
    load_dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    from dotenv import load_dotenv
    load_dotenv(load_dotenv_path)
    
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "redline_cult")
    
    manager = MongoManager()
    manager.initialize(uri, db_name)
    db = manager.get_db()
    
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    
    # 1. Ideas
    ideas_path = os.path.join(repo_root, "memory/ideas.md")
    if os.path.exists(ideas_path):
        with open(ideas_path, "r") as f:
            ideas = parse_ideas(f.read())
            if ideas:
                db.ideas.insert_many([i.model_dump() for i in ideas])
                print(f"Migrated {len(ideas)} ideas.")

    # 2. Videos
    videos_dir = os.path.join(repo_root, "memory/videos")
    if os.path.exists(videos_dir):
        v_count = 0
        for f_name in os.listdir(videos_dir):
            if f_name.endswith(".md"):
                with open(os.path.join(videos_dir, f_name), "r") as f:
                    video = parse_video(f.read())
                    db.videos.insert_one(video.model_dump())
                    v_count += 1
        print(f"Migrated {v_count} videos.")

if __name__ == "__main__":
    migrate()

import os
import json
import glob
import random
import requests
import shutil
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Import upload functions
try:
    from upload.upload_instagram import upload_to_instagram
    from upload.upload_threads import upload_to_threads
    from upload.upload_facebook import upload_to_facebook, upload_to_facebook_story
    from upload.upload_to_youtube import upload_to_youtube
except ImportError as e:
    print(f"Error importing upload modules: {e}")
    # Still want to proceed or stop?
    pass

PROCESSED_DIR = "Processed_Videos"
PUBLISHED_LOG = "published_videos.json"

def get_already_published():
    if os.path.exists(PUBLISHED_LOG):
        with open(PUBLISHED_LOG, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def get_repost_counts():
    """Count how many times each video has been posted."""
    published = get_already_published()
    counts = {}
    for entry in published:
        vname = entry.get("video_name", "")
        counts[vname] = counts.get(vname, 0) + 1
    return counts

def mark_as_published(video_name, metadata):
    published = get_already_published()
    published.append({
        "video_name": video_name,
        "metadata": metadata
    })
    with open(PUBLISHED_LOG, 'w', encoding='utf-8') as f:
        json.dump(published, f, indent=4)

def select_video(specific_video=None):
    published = [item["video_name"] for item in get_already_published()]
    all_videos = sorted(glob.glob(os.path.join(PROCESSED_DIR, "*.mp4")))

    if specific_video:
        # specific_video might be a full path or just a filename
        if os.path.exists(specific_video):
            # It's a full path
            vid_path = specific_video
            name = os.path.basename(specific_video)
        else:
            # It's just a filename, join with PROCESSED_DIR
            vid_path = os.path.join(PROCESSED_DIR, specific_video)
            name = specific_video

        if os.path.exists(vid_path):
            if name in published:
                post_count = sum(1 for p in published if p == name)
                print(f"🔄 Video {name} was already published ({post_count}x) - Re-publishing (recycling)")
            return vid_path, name
        else:
            print(f"❌ Error: Specific video {name} not found")
            return None, None

    # Find unpublished videos first
    unpublished = [(vid, os.path.basename(vid)) for vid in all_videos if os.path.basename(vid) not in published]

    if unpublished:
        vid, name = unpublished[0]
        return vid, name

    # All videos published - use weighted random selection (less posted = more likely)
    if all_videos:
        repost_counts = get_repost_counts()
        weights = []
        for vid in all_videos:
            name = os.path.basename(vid)
            count = repost_counts.get(name, 0)
            weight = max(1, 1000 // (3 ** min(count, 6)))
            weights.append(weight)

        selected_vid = random.choices(all_videos, weights=weights, k=1)[0]
        name = os.path.basename(selected_vid)
        post_count = repost_counts.get(name, 0)
        print(f"🎲 All videos published. Weighted random reuse (posted {post_count}x): {name}")
        return selected_vid, name

    return None, None

def generate_caption():
    import random
    import time

    api_key = os.getenv("POLLINATIONS_API_KEY")
    model = os.getenv("AI_MODEL", "openai")

    fallback_titles = [
        "The Lion That Defied the Odds — Unbelievable Rescue Story",
        "Watch a Baby Elephant Take Its First Steps in the Wild",
        "Close Encounter with a Cheetah at Full Speed",
        "Hyenas vs Lions — The Ultimate Showdown",
        "A Rhino Mother Protecting Her Calf from Danger",
        "Stunning Aerial View of the Serengeti at Sunrise",
        "The Secret Lives of Meerkats in the Kalahari",
        "A Leopard Drags Prey Up a Tree in Seconds",
        "Zebra Migration Across Crocodile-Infested Waters",
        "Hippos: The Most Dangerous Animals You Didn't Expect",
        "Wildebeest Stampede — Pure Raw Power of Nature",
        "A Baby Giraffe Learning to Walk Minutes After Birth",
        "The African Wild Dog — Nature's Most Efficient Hunter",
        "Witness the Raw Beauty of African Sunsets in the Savannah",
        "Buffalo Takes on a Pride of Lions — Who Will Win?",
    ]

    fallback_descriptions = [
        "The African wilderness is full of unbelievable moments. Watch this incredible rescue as a lion cub finds its way back to the pride after being separated. Nature is raw, unpredictable, and absolutely breathtaking. Every single animal has a story to tell. Like if you love wildlife and follow Wildsafari Cubs for more incredible safari moments! 🦁 #wildlife #safari #africa #lion #nature #wildanimals #savannah #bigcats #animals #naturelovers #conservation #wildsafaricubs",
        "There's nothing more magical than witnessing new life in the wild. This baby elephant takes its first wobbling steps and the herd surrounds it with protection. Elephants have the strongest family bonds in the animal kingdom. Truly heartwarming. Drop a 🐘 if you love these gentle giants! #elephant #wildlife #safari #nature #africa #babyanimals #savannah #animals #wildsafaricubs #conservation",
        "Cheetahs are nature's speed machines — reaching 70 mph in just 3 seconds. Watch this incredible predator in action as it stalks through the golden grass of the savannah. Pure athletic perfection. The fastest land animal on Earth is a sight you'll never forget. Double tap if you're amazed by these beautiful cats! 🐆 #cheetah #wildlife #safari #speed #bigcats #africa #nature #predator #animals #wildsafaricubs",
        "The eternal battle between hyenas and lions plays out on the African plains every single day. This clash is intense as a clan of hyenas challenges a lion pride over a fresh kill. The wild is unforgiving and every meal is earned through strength and strategy. Who were you rooting for? Comment below! 🦁 #lions #hyenas #wildlife #safari #africa #nature #predator #showdown #animals #wildsafaricubs",
        "A mother rhino's love knows no bounds. When danger approaches her calf, she charges without hesitation. Rhinos may look tough but they are incredibly protective parents. We must protect these magnificent creatures from extinction. Like if you stand against poaching! 🦏 #rhino #wildlife #conservation #safari #africa #nature #endangeredspecies #animals #protection #wildsafaricubs",
        "The Serengeti at golden hour is nothing short of heaven on Earth. Watch this breathtaking aerial view as the sun rises over the vast African plains. Miles of untouched wilderness stretching as far as the eye can see. This is why we go on safari. Save this video for your daily dose of peace! 🌅 #serengeti #safari #africa #sunrise #nature #travel #landscape #wilderness #wildsafaricubs",
        "Meerkats are some of the most adorable and intelligent creatures in the Kalahari. Watch them work together as a team — taking turns standing guard, foraging for food, and caring for their young. Their social structure is fascinating. Every meerkat has a job to do! Follow for more amazing wildlife stories! 🐾 #meerkat #wildlife #kalahari #africa #nature #animals #cute #safari #wildsafaricubs",
        "A leopard's strength is unmatched — watch it drag a kill twice its own weight up a tree in seconds. This is how leopards protect their food from lions and hyenas. Stealth, power, and precision all in one magnificent cat. Absolutely jaw-dropping. Comment 🔥 if you respect the leopard's power! #leopard #wildlife #safari #bigcats #africa #nature #predator #strength #animals #wildsafaricubs",
        "The great zebra migration is one of the most dangerous journeys on Earth. Thousands of hooves thunder across the river as crocodiles lurk beneath the surface. Only the strong survive. This is nature at its most raw and real. Every year they risk everything for fresh grazing land. Like if you're amazed by their courage! 🦓 #zebra #migration #wildlife #safari #africa #nature #survival #animals #wildsafaricubs",
        "Don't be fooled by their cute appearance — hippos are the deadliest large animals in Africa. Watch this incredible footage of a hippo defending its territory in the water. They are responsible for more human fatalities than any other large African animal. Respect the wild from a distance! 🦛 #hippo #wildlife #safari #africa #dangerous #animals #nature #river #wildsafaricubs",
        "Feel the ground shake as thousands of wildebeest stampede across the Mara River. The raw power of nature in motion is something you have to witness to believe. Dust, thunder, and determination — the wildebeest migration is the greatest wildlife show on Earth. Comment if this gave you chills! 🌪️ #wildebeest #migration #wildlife #safari #africa #nature #serengeti #animals #wildsafaricubs",
        "One of the most beautiful moments in nature — a baby giraffe taking its first steps just minutes after being born. Giraffes give birth standing up, so the calf drops over 6 feet to the ground! And within an hour it's walking. Nature is incredible. Drop a 🦒 if you love giraffes! #giraffe #wildlife #babyanimals #safari #africa #nature #savannah #animals #cute #wildsafaricubs",
        "African wild dogs are the most successful hunters in Africa — with an 80% kill rate. Watch this pack work together with incredible coordination and intelligence. Every member has a role and they communicate constantly. Teamwork at its finest in the animal kingdom. Follow Wildsafari Cubs for more incredible wildlife content! 🐕 #africanwilddog #wildlife #safari #hunting #africa #nature #predator #pack #animals #wildsafaricubs",
        "There is nothing quite like an African sunset over the savannah. The golden light, the silhouette of acacia trees, the distant call of a lion. This is what we live for. Moments like this remind us how beautiful our planet truly is. Save this video for when you need a moment of peace. 🌍 #sunsets #safari #africa #nature #landscape #savannah #beauty #travel #peace #wildsafaricubs",
        "A lone buffalo takes on an entire pride of lions in a fight for survival. The cape buffalo is one of the most dangerous animals in Africa — known as the Black Death. This showdown is intense, brutal, and absolutely captivating. Nature is not a fairy tale — it's survival. Who wins this battle? Watch till the end! 🐃 #buffalo #lions #wildlife #safari #africa #nature #survival #predator #showdown #wildsafaricubs",
    ]

    if not api_key:
        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        print("Warning: POLLINATIONS_API_KEY not found. Using fallback captions.")
        return chosen_title, chosen_desc

    vibes = [
        "awe-inspiring and breathtaking — make viewers feel the raw beauty of the African wilderness",
        "educational and fascinating — share incredible animal facts that make people stop and stare",
        "heartwarming and emotional — tell stories of family bonds, survival, and love in the animal kingdom",
        "adrenaline-pumping and intense — capture the drama and danger of predator-prey encounters",
        "peaceful and meditative — transport viewers to the golden savannah with stunning visuals",
        "funny and surprising — show the playful, unexpected side of wild animals",
        "powerful and majestic — highlight the strength, grace, and beauty of Africa's greatest creatures",
    ]
    chosen_vibe = random.choice(vibes)

    prompt = (
        f"Write a completely unique, long, and captivating title and description for a short video "
        f"for the social media page 'Wildsafari Cubs'. "
        f"The page showcases breathtaking African wildlife and safari adventures — from the majestic Big Five to the smallest creatures of the savannah. "
        f"It's all about the raw beauty of nature, animal behavior, conservation, and the thrill of the wild. "
        f"Make the vibe {chosen_vibe}. "
        f"The description should be LONG (4-6 sentences minimum), deeply engaging, and vivid. "
        f"Include engagement calls-to-action such as: "
        f"- Like if you love wildlife! "
        f"- Comment your favorite African animal! "
        f"- Share with a fellow nature lover! "
        f"- Follow Wildsafari Cubs for more incredible safari moments! "
        f"Include relevant hashtags in ALL LOWERCASE such as #wildlife #safari #africa #nature #wildanimals #savannah #bigcats #conservation #lion #elephant #giraffe #zebra #wildsafaricubs #animals #travel. "
        f"Return ONLY a valid JSON object in this format: {{\"title\": \"<title>\", \"description\": \"<description>\"}} "
        f"Do not include any other text or markdown block backticks."
    )

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "seed": random.randint(1, 999999)
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)

        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        return result.get("title", chosen_title), result.get("description", chosen_desc)
    except Exception as e:
        print(f"Error generating caption: {e}")
        return random.choice(fallback_titles), random.choice(fallback_descriptions)

def main():
    print("=" * 60)
    print("🚀 DAILY AUTOMATION STARTING")
    print("=" * 60)
    
    specific_video = sys.argv[1] if len(sys.argv) > 1 else None
    video_path, video_name = select_video(specific_video)
    if not video_path:
        print("✅ No new videos found to publish. Exiting.")
        return
        
    print(f"👉 Selected Video: {video_name}")
    print("🧠 Generating caption via Pollination AI...")
    title, description = generate_caption()
    
    print(f"📝 Title: {title}")
    print(f"📝 Description:\n{description}")
    
    # Combined caption for platforms that use a single text field
    combined_caption = f"{title}\n\n{description}"
    
    success_flags = {
        "instagram_reel": False,
        "instagram_story": False,
        "facebook_reel": False,
        "facebook_story": False,
        "threads": False,
        "youtube": False
    }
    
    # Instagram Reels
    try:
        result = upload_to_instagram(video_path, combined_caption, is_story=False)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Instagram Reel: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["instagram_reel"] = True
    except Exception as e:
        print(f"❌ Instagram Reel upload failed: {e}")
        
    # Instagram Stories
    try:
        result = upload_to_instagram(video_path, combined_caption, is_story=True)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Instagram Story: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["instagram_story"] = True
    except Exception as e:
        print(f"❌ Instagram Story upload failed: {e}")
        
    # Facebook Reels
    try:
        result = upload_to_facebook(video_path, description, title=title)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Facebook Reel: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["facebook_reel"] = True
    except Exception as e:
        print(f"❌ Facebook Reel upload failed: {e}")
        
    # Facebook Stories
    try:
        result = upload_to_facebook_story(video_path)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Facebook Story: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["facebook_story"] = True
    except Exception as e:
        print(f"❌ Facebook Story upload failed: {e}")
        
    # Threads
    try:
        result = upload_to_threads(video_path, combined_caption)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Threads: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["threads"] = True
    except Exception as e:
        print(f"❌ Threads upload failed: {e}")
        
    # YouTube Shorts
    try:
        upload_to_youtube(video_path, title, description, tags=["wildlife", "safari", "africa", "nature", "wildanimals", "savannah", "lion", "elephant", "giraffe", "cheetah", "zebra", "rhino", "leopard", "bigcats", "conservation", "animals", "wildsafaricubs"])
        success_flags["youtube"] = True
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        
    # Record as published regardless of partial success,
    # to avoid repeating the same video. Alternatively, only record if fully successful.
    print("\n✅ Marking video as published.")
    
    # Check if this is a recycled video (already in published_videos.json)
    published_list = get_already_published()
    is_recycled = any(item["video_name"] == video_name for item in published_list)
    
    if is_recycled:
        print(f"   🔄 This is a recycled video (re-publishing)")
    
    mark_as_published(video_name, {
        "title": title,
        "description": description,
        "success_flags": success_flags,
        "recycled": is_recycled
    })
    
    # Move the published video to Published_Videos folder
    published_dir = "Published_Videos"
    if not os.path.exists(published_dir):
        os.makedirs(published_dir)
        
    try:
        dest_path = os.path.join(published_dir, video_name)
        shutil.move(video_path, dest_path)
        print(f"📦 Moved published video to {dest_path}")
    except Exception as e:
        print(f"❌ Failed to move published video: {e}")
    
    print("🎉 DAILY AUTOMATION COMPLETE")

if __name__ == "__main__":
    main()

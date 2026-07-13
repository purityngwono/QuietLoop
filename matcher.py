import re

# ===== EMOJI + SLANG NORMALIZATION =====
def normalize_message(text):
    # Remove emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F" # emoticons
        u"\U0001F300-\U0001F5FF" # symbols & pictographs
        u"\U0001F680-\U0001F6FF" # transport & map
        u"\U0001F1E0-\U0001F1FF" # flags
        u"\U00002702-\U000027B0" # dingbats
        u"\U000024C2-\U0001F251" # enclosed
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub('', text)
    
    # Lowercase
    text = text.lower()
    
    # Slang mapping
    slang = {
        "u": "you", "r": "are", "ur": "your", "4": "for",
        "2": "to", "plz": "please", "thx": "thanks",
        "idk": "i don't know", "tbh": "to be honest",
        "rn": "right now", "nvm": "never mind",
        "brb": "be right back", "lol": "laughing",
        "omg": "oh my god", "smh": "shaking my head",
        "imo": "in my opinion", "btw": "by the way",
        "ikr": "i know right", "wyd": "what are you doing",
        "hmu": "hit me up", "fyi": "for your information",
        "np": "no problem", "yw": "you're welcome"
    }
    for s, r in slang.items():
        text = text.replace(s, r)
    
    return text

# ===== TOPICS FOR MATCHING =====
topics = {
    "loneliness": [
        "alone", "lonely", "loneliness", "isolated", "invisible", 
        "nobody", "no one", "empty", "unseen", "forgotten", 
        "feel lonely", "all alone", "by myself", "no friends"
    ],
    "anxiety": [
        "anxious", "anxiety", "worried", "stress", "panic", 
        "scared", "fear", "overwhelmed", "nervous", "on edge",
        "freaking out", "can't breathe", "racing heart"
    ],
    "hope": [
        "hope", "future", "believe", "dream", "wish", 
        "better", "optimistic", "looking forward", "positive"
    ],
    "grief": [
        "lost", "gone", "miss", "grief", "death", 
        "passed", "heartbroken", "sad", "sorrow", "mourning"
    ],
    "joy": [
        "happy", "grateful", "blessed", "joy", "thankful", 
        "wonderful", "excited", "proud", "blessed", "amazing"
    ],
    "anger": [
        "angry", "mad", "frustrated", "fed up", "tired of", 
        "annoyed", "resentful", "furious", "rage", "irritated"
    ],
    "love": [
        "love", "care", "heart", "special", "cherish", 
        "affection", "admire", "adore", "passion"
    ],
    "confusion": [
        "confused", "lost", "don't know", "uncertain", 
        "maybe", "unsure", "doubt", "mixed up", "puzzled"
    ],
}

def detect_topic(message):
    clean_msg = normalize_message(message)
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in clean_msg:
                return topic
    return "general"

# ===== MOOD KEYWORDS (for returning greeting) =====
mood_keywords = {
    "lonely": ["lonely", "loneliness", "alone", "isolated", "invisible"],
    "anxious": ["anxious", "anxiety", "worried", "stress", "panic"],
    "sad": ["sad", "cry", "crying", "sadness", "grief", "sorrow"],
    "tired": ["tired", "exhausted", "drained", "overwhelmed"],
    "hopeful": ["hope", "hopeful", "optimistic", "better", "positive"],
    "angry": ["angry", "mad", "frustrated", "resentful", "rage"],
    "grateful": ["grateful", "thankful", "blessed", "appreciate"]
}

def extract_mood(message):
    clean_msg = normalize_message(message)
    for mood, keywords in mood_keywords.items():
        if any(k in clean_msg for k in keywords):
            return mood
    return "neutral"

# ===== HEAVY MESSAGE DETECTION =====
heavy_keywords = [
    "lonely", "loneliness", "depressed", "depression", 
    "anxious", "anxiety", "scared", "fear", "afraid",
    "hurts", "hurting", "pain", "sad", "cry", "crying",
    "tired", "exhausted", "overwhelmed", "hopeless",
    "worthless", "useless", "failure", "lost", "empty",
    "trauma", "traumatized", "broken", "dying", "suffering",
    "grief", "grieving", "heartbroken", "alone", "isolated"
]

def is_heavy_message(message):
    clean_msg = normalize_message(message)
    return any(keyword in clean_msg for keyword in heavy_keywords) or len(clean_msg) > 40

# ===== CRISIS KEYWORDS =====
crisis_keywords = [
    "suicidal", "suicide", "kill myself", "end my life",
    "want to die", "don't want to live", "better off dead",
    "i can't go on", "no reason to live", "wish i was dead",
    "take my life", "end it all", "give up on life"
]

def is_crisis(message):
    clean_msg = normalize_message(message)
    return any(keyword in clean_msg for keyword in crisis_keywords)

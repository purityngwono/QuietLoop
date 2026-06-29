topics = {
    "loneliness": ["alone", "lonely", "isolated", "invisible", "nobody", "no one"],
    "anxiety": ["anxious", "worried", "stress", "panic", "scared", "fear"],
    "hope": ["hope", "future", "believe", "dream", "wish", "better"],
    "grief": ["lost", "gone", "miss", "grief", "death", "passed"],
    "joy": ["happy", "grateful", "blessed", "joy", "thankful", "wonderful"],
    "anger": ["angry", "mad", "frustrated", "fed up", "tired of"],
    "love": ["love", "care", "heart", "special", "cherish"],
    "confusion": ["confused", "lost", "don't know", "uncertain", "maybe"],
}

def detect_topic(message):
    message_lower = message.lower()
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in message_lower:
                return topic
    return "general"

import random
import time

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == "":
        return random.choice([
            "Bro if ur pinging me say something",
            "Cmon if ur pinging me i want to hear smth",
            "bro dont ping me if u dont have anything to tell me anyway"
        ])
    elif "hello" in lowered or "hi" in lowered:
        return random.choice([
            "help me im stuck in maggies basement",
            "yo sup",
            "hello",
            "yoooooo",
            "sup?"
        ])
    elif "bye" in lowered or "cya" in lowered:
        return random.choice([
            "cya",
            "oki bye :)",
            "later :)",
            "bb",
            "cya later"
        ])
    elif "how are you" in lowered or "hru" in lowered:
        return random.choice([
            "im good thx",
            "good hbu?",
            "pretty well, thx",
            "not bad",
            "im fine"
        ])
    elif "cn" in lowered or "craftnite" in lowered:
        return random.choice([
            "i love cn",
            "cn is best game of all time",
            "i especially love cheating in cn XD"
        ])
    else:
        return random.choice([
            "i didnt quiet get that",
            "buddy u need to learn how to communicate with ppl like me",
            "im not smart enough to get that XD",
            "im not getting paid minimum wage to understand your shittalk",
            "i dont know what ur saying :P",
            "can you plsssss try smth else? i dont want to waste my time on figuring ur sentence out",
            "what r u trying to achieve with this nonsense",
            "buddy, ur grammar is terrible. can u make it a bit better?",
            "just try smth simpler plssss :)))))"
        ])
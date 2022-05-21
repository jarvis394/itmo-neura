from random import choice
from typing import Dict, List


START = "__START___"
END = "__END___"


def generate(samples: List[str], attempts: int, max_length: int = None):
    if not samples:
        return None

    frames: List[str] = []
    start_frames: List[str] = []
    frame_map: Dict[str, List[str]] = {}

    for sample in samples:
        sample_words = sample.split(" ")
        frames.append(START)
        for word in sample_words:
            frames.append(word)
        frames.append(END)

    for i in range(len(frames)):
        if frames[i] != END:
            if frames[i] in frame_map:
                frame_map[frames[i]].append(frames[i + 1])
            else:
                frame_map[frames[i]] = [frames[i + 1]]

            if frames[i] == START:
                start_frames.append(frames[i + 1])

    for i in range(attempts):
        words = [choice(start_frames)]

        for frame in words:
            next_frame = choice(frame_map[frame])
            if next_frame == END or (max_length != None and len(words) >= max_length):
                break
            else:
                words.append(next_frame)

        sentence = " ".join(words)

        if sentence not in samples and len(words) <= 50:
            return sentence

    return None

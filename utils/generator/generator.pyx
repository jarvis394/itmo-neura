from random import choice


cdef str START = "__START___"
cdef str END = "__END___"


def generate(list samples, int attempts):
    if not samples:
        return None

    cdef list frames = []
    cdef list start_frames = []
    cdef dict frame_map = {}
    cdef list sample_words
    cdef list words
    cdef str sentence
    cdef str next_frame
    cdef str sample
    cdef int i

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
            if next_frame == END: break
            else: words.append(next_frame)

        sentence = " ".join(words)

        if sentence not in samples and len(words) <= 50:
            return sentence

    return None

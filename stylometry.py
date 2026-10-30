"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies.

    Returns:
        The coefficient of variation of sentence lengths (stdev / mean, in
        words-per-sentence) — unitless, so a long text and a short one are
        comparable. Direction: HIGHER means MORE HUMAN. Generated prose tends
        toward even, mid-length sentences; human writing puts a three-word
        sentence next to a forty-word one.

    Fewer than two sentences has no spread to measure — returns 0.0, which
    reads as "as uniform as possible" rather than raising.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return statistics.stdev(lengths) / mean


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words.

    Returns:
        A float between 0 and 1. Direction: HIGHER means MORE HUMAN (more
        varied vocabulary). Generated prose draws from a narrower band of
        likely words.

    Falls as text gets longer regardless of authorship, because common words
    repeat — texts of very different lengths aren't directly comparable on
    this measure alone.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    How much of the "interesting" punctuation shows up, relative to length.

    Returns:
        Count of semicolons, colons, parentheses, and em/en dashes, per word.
        Direction: HIGHER means MORE HUMAN. These marks vary a lot between
        individual writers and rarely show up by accident; plain generated
        prose tends to lean on commas and periods instead.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    marks = re.findall(r"[;:()–—]", text)
    return len(marks) / len(tokens)


# ── Combining them ───────────────────────────────────────────────────────────

# Higher values in these measurements suggest more human-like writing.
# I flip the scores so a higher final score means more AI-like writing.
# The ceilings are a judgment call, picked by running calibration text through
# this module and seeing where real values land — not derived from theory.
# Change them if your own calibration texts suggest different numbers, and say
# so in the README.
_SPREAD_CEILING = 0.8     # coefficient of variation at/above which "fully human-spread"
_PUNCT_CEILING = 0.06     # "interesting" punctuation marks per word, at the human end


def _normalize(value: float, ceiling: float) -> float:
    """Scale a raw measure to 0-1 against a ceiling, clipped at both ends."""
    if ceiling <= 0:
        return 0.0
    return max(0.0, min(1.0, value / ceiling))


def style_signal(text: str) -> float:
    """
    Combines the three writing-style measurements.
    Returns a score between 0 and 1.
    Higher scores mean the text looks more AI-like.
    """
    spread_ai = 1.0 - _normalize(sentence_length_spread(text), _SPREAD_CEILING)
    ttr_ai = 1.0 - type_token_ratio(text)  # already 0-1, no ceiling needed
    punct_ai = 1.0 - _normalize(punctuation_density(text), _PUNCT_CEILING)

    score = (spread_ai + ttr_ai + punct_ai) / 3.0
    return round(max(0.0, min(1.0, score)), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    

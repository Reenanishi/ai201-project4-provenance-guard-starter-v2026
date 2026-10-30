"""
Turning two numbers into one, and one number into something a person can read.
← YOU BUILD THIS IN MILESTONES 4 AND 5

Two functions live here, and both are stubs.

`combine_signals` is where your false-positive decision from Milestone 1
actually gets made. Everything above it — the labels, the appeal path — is
downstream of a number this function produced.

`score_to_label` is where you stop writing for a machine and start writing for
a person. A score of 0.62 means nothing to a writer.

⚠️ Your README's **Signals and Scoring** section has to name the file and
function holding your combining rule. The grader checks your code against what
you claim, so that line should read `scoring.py::combine_signals`.
"""

import config


def combine_signals(model_score: float, style_score: float) -> float:
    """
    Combine two 0-1 signals into one 0-1 score. Both inputs point the same
    way — higher means more likely AI — and so does the output.

    **The rule:** a plain weighted average, 0.5/0.5
    (`config.WEIGHT_MODEL_SIGNAL` / `config.WEIGHT_STYLE_SIGNAL`).

    **Why:** checked against four calibration inputs (Milestone 4) — the two
    that split, formal human writing and lightly-edited AI text, both land
    away from a wrong accusation under a plain average (formal human -> 0.558,
    squarely "unsure"; edited AI -> 0.298, "human" — a miss, but not a false
    accusation). A rule that leans further toward whichever signal reads more
    human didn't change either outcome on this data, so it isn't earning its
    extra constant. Averaging is also the plainest way to treat "the two
    signals disagree" as what it actually is: uncertainty, not a tiebreak.
    """
    return round(
        config.WEIGHT_MODEL_SIGNAL * model_score
        + config.WEIGHT_STYLE_SIGNAL * style_score,
        4,
    )


def score_to_label(score: float) -> tuple[str, str]:
    """
    Turns the final score into a label that people can understand.
    """
    if score >= config.AI_THRESHOLD:
        return "ai", "This writing shows strong signs of AI-generated text. This result is not proof."

    if score <= config.HUMAN_THRESHOLD:
        return "human", "This writing looks more likely to be human-written."

    return "unsure", "We cannot confidently tell whether this writing was created by a person or AI."



def label_ranges() -> list[tuple[str, str]]:
    """
    The score range each label covers. Your README needs these beside the
    label text — given to you so the numbers can't drift apart from config.py.
    """
    return [
        ("high-confidence human", f"0.00 – {config.HUMAN_THRESHOLD:.2f}"),
        ("unsure", f"{config.HUMAN_THRESHOLD:.2f} – {config.AI_THRESHOLD:.2f}"),
        ("high-confidence AI", f"{config.AI_THRESHOLD:.2f} – 1.00"),
    ]

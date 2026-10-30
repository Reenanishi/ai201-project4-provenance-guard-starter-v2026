# Milestone 1 — Trace a submission before you build one

Not graded directly, not one of the three submission artifacts — this is the
paper trace the brief asks for before any code. Fill it in yourself; it's the
scratch work behind `criteria.md` and the README sections later.

---

## 1. The path

<!-- 6-7 steps, plain English: what a piece of text passes through from
     hitting /submit to the label a reader sees, and what each step adds. -->



---

## 2. The two signals

### Signal one — the model (`detector.py`)

**What it measures:**

**Why that might differ between human and AI writing:**

**What it can't see (the blind spot):**

### Signal two — style (`stylometry.py`, yours to build)

**What it measures:**

**Why that might differ between human and AI writing:**

**What it can't see (the blind spot):**

---

## 3. Trace the false positive

<!-- A real writer submits real work. Your system calls it AI. Follow them
     through the service: what score did they get, what did the label say,
     what can they do about it? -->

**Who they are:**

**What score they get and why:**

**What the label says to them:**

**What they can do about it:**

---

## 4. The two endpoint shapes

<!-- Field by field. Could someone else build against this without asking
     you a question? -->

### `POST /submit`

**In:**

**Out:**

### `POST /appeal`

**In:**

**Out:**

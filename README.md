# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

For this project, I built a Flask app called Provenance Guard that checks if a piece of writing might be AI-generated or human-written.

When someone submits their writing, this is what happens:

1. The user sends their text and creator ID to the `/submit` endpoint.
2. The app checks if the required information is there.
3. The first signal looks at how predictable the text is using a language model.
4. The second signal looks at writing style, like sentence lengths, word variety, and punctuation.
5. Both scores are combined, with each one counting for 50% of the final score.
6. Based on the final score, the app gives one of three results: `human`, `unsure`, or `ai`.
7. The result is saved in the audit log so it can be checked later.

I also added an `/appeal` endpoint. If someone disagrees with their result, they can explain why and request a review. The app saves their appeal with the status `under_review`.

I know that AI detection is not always accurate, so I included an `unsure` result instead of forcing every submission to be labeled as human or AI.

---

## Signals and Scoring


### Signal one — the model signal

**What it measures:**
The first signal uses GPT-2 to check how predictable the writing is. It gives a score between 0 and 1. A higher score means the text looks more like AI writing.

**Why that might differ between human and AI writing:**
AI writing can sometimes follow patterns that are easier for a language model to predict. Human writing can be less predictable because people have different ways of expressing themselves.

**What it can't see:**
This signal cannot actually know who wrote the text. A person might write something that sounds very organized or predictable, and the model could mistake it for AI writing.

### Signal two — the style signal

**What it measures:**
The second signal looks at sentence lengths, word variety, and punctuation. It checks how much these things change throughout the writing.

**Why that might differ between human and AI writing:**
AI writing can sometimes have similar sentence lengths and repeated patterns. Human writing might have more variation, but that is not always true.

**What it can't see:**
Some people naturally write in a very consistent style. Also, someone can edit AI-generated text to make it sound different. This signal might not work as well with very short writing samples.

### The combining rule

**The rule:**
I decided to give both signals equal importance instead of depending on just one.

**The numbers:**
combined_score = (0.5 * model_score) + (0.5 * style_score)

The final score is rounded to four decimal places.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**
I tested this text:

"I was tired. Yesterday I walked all the way to school because I missed the bus. Done!"

These were my results:

Model score: 0.4994

Style score: 0.3922

Combined score: 0.4458

Final result: unsure

The model score was a little higher than the style score, so the two signals did not completely agree. Since I gave them equal weight, the final score ended up between them.

I think this is better than trusting only one signal because neither one is perfect. If the app is not confident, I would rather have it say unsure than incorrectly label someone's writing as AI-generated.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 to 0.35 (including 0.35) | This writing looks more likely to be human-written. |
| unsure |Above 0.35 but below 0.65 |We cannot confidently tell whether this writing was created by a person or AI. |
| high-confidence AI |0.65 to 1.00 (including 0.65) |This writing shows strong signs of AI-generated text. This result is not proof.|

**Why I worded the "unsure" one this way:**

I wanted the unsure message to be fair to the person submitting their writing. The app cannot always tell whether something was written by AI or a human. Instead of making a wrong accusation, I think it is better to say that the result is uncertain. Just because someone's writing looks similar to AI writing does not mean they used AI.

---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

I tested my app by submitting a short piece of writing. I used port 5001 because port 5000 was already being used on my Mac.


```bash
curl -X POST http://127.0.0.1:5001/submit \
  -H "Content-Type: application/json" \
  -d '{"text":"I was tired. Yesterday I walked all the way to school because I missed the bus. Done!","creator_id":"student1"}'
```

```json
{
  "confidence": 0.4458,
  "content_id": "ddb2133e-7576-44dc-b7f6-f68ec0519ecc",
  "guess": "unsure",
  "label": "We cannot confidently tell whether this writing was created by a person or AI.",
  "model_score": 0.4994,
  "style_score": 0.3922
}
```

**An appeal**
I also tested the appeal feature to make sure someone could ask for their result to be reviewed.

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "ddb2133e-7576-44dc-b7f6-f68ec0519ecc", "reasoning": "I wrote this myself and would like someone to review the result."}'
```

```json
{
  "content_id": "ddb2133e-7576-44dc-b7f6-f68ec0519ecc",
  "status": "under_review",
  "message": "Your appeal has been recorded and is awaiting review."
}
```
The app recorded the appeal and changed its status to under_review. It does not automatically change the original result.

**What the log shows afterwards**
I checked the audit log to make sure both the submission and the appeal were saved.



```bash
$ curl "http://127.0.0.1:5001/log?limit=2"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.4458,
      "content_id": "ddb2133e-7576-44dc-b7f6-f68ec0519ecc",
      "creator_id": "student1",
      "guess": "unsure",
      "label": "We cannot confidently tell whether this writing was created by a person or AI.",
      "model_score": 0.4994,
      "status": "decided",
      "style_score": 0.3922,
      "timestamp": "2026-10-30T21:02:46+00:00"
    },
    {
      "content_id": "ddb2133e-7576-44dc-b7f6-f68ec0519ecc",
      "creator_id": "student1",
      "event": "appeal",
      "reasoning": "I wrote this myself and would like someone to review the result.",
      "status": "under_review",
      "timestamp": "2026-10-30T21:03:11+00:00"
    }
  ]
}
```
The log shows that my submission was saved first and my appeal was saved after that. Both entries have the same content_id, which shows they are connected.

---

## How I Used AI

**Moment 1**

- *What I asked for:*
I used ChatGPT to help me understand some parts of the code and check for errors.
- *What came back:*
It gave me explanations and suggestions for fixing problems.
- *What I changed:*
I checked the suggestions and tested my code to see if it worked.

**Moment 2**

- *What I asked for:*
I used Claude and ChatGPT to help test my project.
- *What came back:*
They suggested ways to test the submission, scoring, and appeal features.
- *What I changed:*
I ran the tests in my terminal and checked the responses and audit log.


### Bonus Feature Planned: GET /content/<id>

I plan to add an endpoint that lets someone check the current status of a submission using its content ID. I will test it and include the request and response here.

#### Bonus Feature Test

I added a GET /content/<id> endpoint in app.py. It looks up a submission in the audit log and returns its latest status. This lets a writer check whether their submission is still decided or under review after an appeal.

Request:

```bash
curl http://127.0.0.1:5001/content/ddb2133e-7576-44dc-b7f6-f68ec0519ecc
```

Response:

```json
{
  "content_id": "ddb2133e-7576-44dc-b7f6-f68ec0519ecc",
  "guess": "unsure",
  "label": "We cannot confidently tell whether this writing was created by a person or AI.",
  "status": "under_review"
}
```


<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

# Annotation Guidelines: Query Type Classification

## What you are doing

You are classifying 30 questions about Stephen King adaptations into one of
three categories. You do not need to know the stories. You only need to
decide what the question is asking.

## The three labels

### EXPLICIT
The question names a specific version by title, year, medium, or director.
The user is directly stating which version they want.

Examples:
- "Does Dick Hallorann survive **in the novel** The Shining?"
- "How is Kurt Barlow depicted **in the 1979 miniseries**?"
- "How does Jack Torrance die **in Kubrick's adaptation**?"

Key signals: "the novel", "the book", "the film", "the 1979 miniseries",
"Kubrick's version", a year, or a director's name.

### IMPLICIT
The question describes a version without naming it. The user refers to a
distinctive detail or attribute that only makes sense for one version.
You have to infer which version from the description.

Examples:
- "In **the version where Jack is a loving but troubled father**, does Hallorann survive?"
- "In **the version where Jack freezes in the hedge maze**, does Hallorann survive?"
- "In **the version that restores over 300 pages**, does The Kid appear?"

Key signals: "the version where...", "the one where...", a description of
a plot event or character trait that distinguishes one version from another.
The question does NOT name a version — it describes one.

### AMBIGUOUS
The question does not name or describe any specific version. It could refer
to any version, and the correct answer depends entirely on which version
the user means.

Examples:
- "Does Dick Hallorann survive The Shining?"
- "What does Kurt Barlow look like?"
- "How does Jack Torrance die?"

Key signals: no version named, no version described. Just the work's title
or a character's name.

## How to decide when unsure

Ask yourself: **If I answered this question, would I need to know which
version the user meant?**

- **Yes, and the user told me → EXPLICIT**
- **Yes, and the user hinted at it without naming it → IMPLICIT**
- **Yes, and the user said nothing → AMBIGUOUS**

If you're still unsure, pick the label that best matches and add a note in
the `notes` column. Do not skip any rows.

## How to fill in your answers

Open `data/annotation_template.csv`. It has three columns:
query_id,label,notes

Fill in the `label` column with one of: `EXPLICIT`, `IMPLICIT`, or `AMBIGUOUS`.
Use all caps, no extra spaces.

The `notes` column is optional. Use it if you were unsure or want to explain.

Do not look up the answers online. Do not ask anyone. Just use the
definitions above.

## After you're done

Save the file and send it back. You do not need to do anything else.
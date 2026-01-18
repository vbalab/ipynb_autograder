You are given the contents of a ground-truth Jupyter notebook solution. Your job is to derive an assessment rubric (task breakdown) based ONLY on what appears in that ground-truth solution.

Output MUST be valid JSON that matches this structure:
{
  "tasks": [
    { "title": string, "description": string, "maximumScore": number }
  ]
}

Rules:

- Create tasks that correspond to distinct parts of the ground-truth notebook task structure.
- If the notebook already defines a grading/points breakdown, mirror it exactly in maximumScore and task boundaries.
- If no grading is provided, assign reasonable maximumScore values and keep them consistent across tasks.
- Do not invent requirements that are not evidenced in the ground-truth notebook.
- Do not include any extra keys besides: title, description, maximumScore.
- Use concise titles and specific, checkable descriptions.

from llm import ask_llm


def clarification_agent(requirement):

    prompt = f"""
You are a software requirement analyst.

Analyze the requirement below.

Requirement:
{requirement}

If information is missing, generate up to 5 clarification questions.

If the requirement is detailed enough, return exactly:

NO_QUESTIONS

Return ONLY:
- NO_QUESTIONS
OR
- A numbered list of questions

Do not explain your reasoning.
"""

    result = ask_llm(prompt, "clarification")
    return result.strip()
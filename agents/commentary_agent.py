from groq import Groq
import os
from memory.commentary_memory import get_history


from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_commentary(insights):
    """
    Generates smart, contextual cricket commentary using memory.
    """

    # 🧠 Get previous commentary (last few lines)
    history_list = get_history()
    history = "\n".join(history_list) if history_list else "No previous commentary."

    # 🎯 Adjust logic based on Match Status & Innings
    match_status_instruction = ""
    state = insights.get("state")
    score1 = insights.get("score1", "")
    score2 = insights.get("score2", "")
    
    if state == "post":
        match_status_instruction = "- The match has FINISHED. Summarize the result or highlight a key performer. Be unique."
    elif state == "pre":
        match_status_instruction = "- The match has NOT started yet. Talk about the upcoming clash and the venue. DO NOT mention scores, targets, or runs needed."
    elif "Yet to bat" in score2:
        match_status_instruction = "- The match is in the 1st INNINGS. Talk about the current run rate, boundaries, or the batting team's start. DO NOT mention runs needed or targets."
    else:
        match_status_instruction = "- The match is in the 2nd INNINGS (The Chase). Mention runs needed, balls left, and the required run rate. Build drama."

    # 🧹 Clean up insights for the prompt to prevent confusion
    clean_insights = insights.copy()
    if state == "pre":
        clean_insights.pop("score1", None)
        clean_insights.pop("score2", None)
    elif "Yet to bat" in score2:
        clean_insights.pop("score2", None)

    # 🎯 Strong prompt for better output
    prompt = f"""
You are a factual IPL cricket commentator.

Strict Rules:
- ONLY use the data provided below. 
- If the match is in {insights.get('venue')}, only say that. Do NOT guess the stadium.
- Do NOT hallucinate scores, player names, or margins. 
- If {insights.get('state')} is 'post', describe the victory EXACTLY as written in 'status'.
- Do NOT say '2-run win' if the status says 'won by 6 wickets'.

Previous commentary:
{history}

Current match data:
{clean_insights}

Instructions:
{match_status_instruction}
- DONT ALWAYS start with 'Ladies and gentlemen'.
- Vary your opening sentence.
- MAX 25 WORDS. Be extremely concise so it fits in 3 lines.
- ONLY talk about THIS specific match. 
- DO NOT mention season records, points table, or 'Xth win of the season' (you don't have that data).
- If the text is cut off, it is a failure. Be punchy.
- Keep it 1 or 2 short sentences max.
- Use a professional, factual, but conversational tone.

Generate commentary:
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a live cricket commentator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )

        commentary = response.choices[0].message.content.strip()
        return commentary

    except Exception as e:
        return f"⚠️ Error generating commentary: {str(e)}"
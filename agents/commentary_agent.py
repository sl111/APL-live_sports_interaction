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

    # 🎯 Adjust logic for Finished Matches
    match_status_instruction = ""
    if insights.get("state") == "post":
        match_status_instruction = "- The match has FINISHED. Summarize a DIFFERENT aspect of the game (e.g. the winner's performance, the close finish, or the venue atmosphere). Be unique."
    else:
        match_status_instruction = "- Mention runs needed, balls left. Build drama if the match is close."

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
{insights}

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
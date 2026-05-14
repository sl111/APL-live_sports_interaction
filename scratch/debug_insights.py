from data.fetch_data import get_match_data
from agents.insight_agent import analyze_match
import json

data = get_match_data()
insights = analyze_match(data)
print(json.dumps(insights, indent=2))

# 🏏 AI Cricket Live: Second-Screen Engagement Dashboard

Transform passive sports viewing into an active, immersive experience. This dashboard is a multi-agent system designed to enhance fan engagement during live cricket matches using real-time data and AI-driven insights.

## 🚀 Key Features

### 1. 🤖 Multi-Agent Intelligence
*   **Live Commentary Agent**: Generates concise, high-impact highlights from real-time match events using Google Gemini/Groq.
*   **Insight Agent**: Analyzes match momentum, calculates the "Pressure Index," and identifies key turning points.
*   **Prediction Agent**: Runs real-time simulations to update victory probabilities and final score projections.

### 2. ⚡ Interactive Fan Zone
*   **Hype Meter**: An emotional pulse-check where fans can "tap to boost" the match hype score with interactive emojis.
*   **Live Wicket Polls**: Real-time community voting on which team will lose the next wicket.
*   **Beat the AI**: A gamified prediction challenge where fans compete against AI projections to guess the final score.

### 3. 🎨 Dynamic Immersive Design
*   **Team-Based Theming**: The entire Fan Zone automatically shifts its color palette (e.g., RCB Red vs. KKR Purple) based on which team is currently batting.
*   **Premium Visuals**: High-contrast "Yellow Card" design system for maximum readability and a professional sport-broadcast feel.
*   **Real-Time Sync**: Auto-refreshing layout ensures fans never miss a ball or a shift in momentum.

## 🛠️ Tech Stack
*   **Frontend**: Streamlit
*   **AI Orchestration**: Google Gemini API / Groq
*   **Data Processing**: Pandas
*   **State Management**: Streamlit Session State & Local Memory

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd google-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys:**
   Create a `.env` file in the root directory and add your keys:
   ```env
   GROQ_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 🏗️ Project Structure
*   `app.py`: Main dashboard layout and CSS styling.
*   `agents/`: Contains the logic for Commentary, Insights, and Prediction agents.
*   `data/`: Handles real-time match data fetching and processing.
*   `memory/`: Manages session-based interaction data (polls, hype, commentary history).

## 🎯 Hackathon Goal
Designed for the **GDG Hackathon**, this project aims to bridge the gap between broadcast television and digital interaction, creating a unified "Second-Screen" environment that keeps fans glued to the game.

---
*Built with ❤️ for Cricket Fans.*

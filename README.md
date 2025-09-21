# 🌸 ikigAI - Ikigai-Powered Career Path Advisor

An AI-powered career guidance application that helps users discover their life's purpose and career path using the Japanese concept of Ikigai.

## 🎯 What is Ikigai?

Ikigai (生き甲斐) is a Japanese concept meaning "a reason for being." It represents the intersection of four fundamental elements:

- **What you love** (Passion)
- **What you are good at** (Skills)
- **What the world needs** (Values/Purpose)
- **What you can be paid for** (Economic viability)

## ✨ Features

### 🔍 Ikigai Assessment
- Comprehensive questionnaire covering skills, passions, values, and economic opportunities
- AI-powered analysis using Google's Gemini API
- Personalized career path recommendations

### 📈 Learning & Development
- Customized upskilling plans based on your Ikigai profile
- Relevant certification and learning resource suggestions
- Skill gap analysis for target careers

### 💼 Market Intelligence
- Real-time job market analysis
- In-demand skills identification
- Career opportunity insights

### 📄 Professional Documents
- AI-generated resume summaries
- Personalized cover letter creation
- Career-focused content optimization

### 🤖 AI Career Counselor
- Interactive chatbot for career guidance
- Context-aware advice based on your Ikigai profile
- 24/7 availability for career questions

### 🏅 Gamification
- Achievement badges for exploration milestones
- Progress tracking system
- Engagement rewards

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Streamlit
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/PunithNS-pixel/ikigAI.git
cd ikigAI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
   - Create a `.streamlit/secrets.toml` file
   - Add your API key:
```toml
GEMINI_API_KEY = "your_api_key_here"
```

4. Run the application:
```bash
streamlit run vi.py
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Engine**: Google Gemini 2.5 Pro
- **Language**: Python
- **Styling**: Custom CSS with Ikigai-themed aesthetics

## 📁 Project Structure

```
ikigAI/
├── vi.py                 # Main Streamlit application
├── .streamlit/
│   └── secrets.toml     # API keys and secrets
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

## 🎨 Design Philosophy

The application features a calm, nature-inspired design that reflects the philosophical nature of Ikigai:

- **Color Palette**: Soft greens and earth tones
- **Typography**: Clean, readable fonts
- **Layout**: Intuitive, guided user experience
- **Interactivity**: Engaging without being overwhelming

## 🔐 Privacy & Security

- API keys are stored securely in environment variables
- No personal data is stored permanently
- All interactions are processed in real-time
- User privacy is prioritized in all features

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the Japanese philosophy of Ikigai
- Powered by Google's Gemini AI
- Built with Streamlit's excellent framework

## 📞 Support

If you have any questions or need assistance, please open an issue on GitHub or contact the maintainer.

---

**Find your purpose. Discover your path. Live your Ikigai.** 🌸
# YojnaMitra (Digital Cyber Cafe)

An AI-powered digital assistance portal designed to bridge the accessibility gap in public welfare scheme enrollment across India. YojnaMitra digitizes and automates traditional "Cyber Cafe" services by providing automated eligibility evaluation, instant identity verification, intelligent form parsing, and contextual conversational guidance.

---

## 🚀 Core Features

* **Proactive "Push" Intelligence:** Instead of manual searching, the algorithm analyzes a citizen's profile and pushes personalized notifications only for schemes they specifically qualify for[cite: 1, 2].
* **End-to-End Automation:** Eliminates long, repetitive forms by securely utilizing stored documents and simulated DigiLocker integrations to automatically map and fill applications[cite: 1, 2].
* **Conversational Consent:** Provides a frictionless chat experience where users learn about a scheme and simply reply "Yes" to trigger the application pipeline[cite: 1, 2].
* **Multi-Persona Engine:** Instantly adapts profiles (e.g., switching from an engineering student's scholarships to a rural farmer's agricultural subsidies) to demonstrate versatility live on stage[cite: 1].
* **Multilingual Support:** Built with native Hindi and English capabilities to break down language barriers for citizens[cite: 3].

---

## 🛠️ System Architecture & Tech Stack

| Component Layer | Technology / Tool | Technical Purpose & Function |
| --- | --- | --- |
| **Frontend Framework** | Streamlit (Python)[cite: 3] | Renders dynamic UI widgets, forms, stateful navigation, and interactive reactive interfaces[cite: 3]. |
| **Data Persistence** | SQLite3 (`yojna_mitra.db`)[cite: 3] | Embedded, serverless database tracking user profiles, application history, and scheme catalogs locally[cite: 3]. |
| **AI / LLM Engine** | OpenAI Python SDK via OpenRouter[cite: 3] | Executes scheme matching, automated document context parsing, and natural language multi-turn assistance[cite: 3]. |
| **Environment Security** | Streamlit Secrets Management[cite: 3] | Secures sensitive deployment parameters and API tokens in TOML format away from public repositories[cite: 3]. |
| **CI/CD & Hosting** | Git, GitHub & Streamlit Cloud[cite: 3] | Automated deployment pipeline triggering environment builds based on remote repository updates[cite: 3]. |

---

## 📂 Project Structure

```text
cyber_cafe/
├── app.py                # Main Streamlit application interface
├── logic.py              # Core AI evaluation, RAG, and matching logic
├── secrets.toml          # Local deployment secrets and API keys
├── requirements.txt      # Python package dependencies
├── yojna_mitra.db        # Local SQLite database for user records & applications
└── README.md             # Project documentation

```

---

## ⚙️ Local Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/chirantan1234shee-ops/cyber_cafe.git
cd cyber_cafe

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Configure Secrets:**
Create a `.streamlit/secrets.toml` file or configure your environment variables with your OpenRouter API key:
```toml
OPENROUTER_API_KEY = "your-api-key-here"

```


4. **Run the application locally:**
```bash
streamlit run app.py

```



---

## 🌐 Links & Demos

* **Live Application:** [yojnamitra-cybercafe.streamlit.app](https://www.google.com/search?q=https://yojnamitra-cybercafe.streamlit.app)[cite: 3]
* **GitHub Repository:** [chirantan1234shee-ops/cyber_cafe](https://www.google.com/search?q=https://github.com/chirantan1234shee-ops/cyber_cafe)

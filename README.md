Recall Triage 🚨

Automated FDA Recall Analysis, Geographic Mapping, and Risk Triage

Recall Triage is an enterprise-grade platform that automates the collection, geographic mapping, and risk analysis of FDA recalls. By analyzing complex recall datasets—such as food contamination from Listeria, dangerous allergens, or foreign objects—Recall Triage enables supply chain managers, retailers, and consumers to immediately identify high-priority local threats and act fast.

📸 Key Features

Geographic Risk Analysis: Cross-references FDA distribution data against target regions (e.g., Texas) to assess immediate local impact.

Automated Urgency Categorization: Classifies recalls into actionable urgency levels, such as "Pull now" versus "Monitor."

Interactive Timeline Replay: Dynamically step through FDA product recall timelines to observe spreading risks over time.

Regional Breakdown Metrics: View top state-level alerts, keyword accuracy stats, and distribution coverage.

Interactive Risk Scoring Tool: Input new variables (e.g., pathogens, allergens, affected lots) to calculate custom risk scores or audit suppliers against our database.

🛠️ Architecture & Tech Stack

Recall Triage is built to run on secure, high-performance infrastructure to ensure the safe processing of critical public safety data from the openFDA Food Enforcement API.

Backend Environment: Hosted on an IBM LinuxONE cloud instance for high-performance computing, cryptographic protection, and enterprise security.

Backend Processing: Python 3 (isolated using a Python virtual environment).

Frontend Interface: Clean, interactive web dashboard accessible via Google Chrome / web browser.

Version Control: GitHub (Trust-Me-Bro repository).

🚀 Getting Started & Local Setup

Follow these steps to connect to the IBM LinuxONE server and run the application locally via SSH port forwarding.

Prerequisites

Private SSH key (.pem / key file) stored locally.

Python 3 installed on the remote instance.

Modern web browser (e.g., Google Chrome).

Step 1: Connect to IBM LinuxONE Server

Open your terminal, navigate to the directory containing your SSH key, and connect to the remote instance:

cd ~/Downloads
ssh -i your-private-key.pem user@your-linuxone-ip


Step 2: Clone Repository & Set Up Virtual Environment

Once connected to the IBM LinuxONE server:

# Clone the repository
git clone https://github.com/Trust-Me-Bro/Recall-Triage.git
cd Recall-Triage

# Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt


Step 3: Boot Up the Application Server

Start the backend web server inside your activated virtual environment:

python app.py


Step 4: Access Dashboard via Port Forwarding

In a second terminal window on your local machine, open an SSH port forwarding tunnel to direct traffic from port 8000 on the LinuxONE server to your local machine:

ssh -N -L 8000:localhost:8000 -i ~/Downloads/your-private-key.pem user@your-linuxone-ip


Open your browser and navigate to:

http://localhost:8000


📊 Using the Dashboard

Timeline Replay: Click "Restart replay" to step through FDA recall events chronologically.

Actionable Urgency Tags: Look for explicit tags like "Pull now" for immediate regional threats (e.g., active distribution in Texas) or "Monitor" for lower-risk/distant items.

Analytics: Scroll down to view regional breakdown charts, top local alerts, and system accuracy statistics.

Interactive Scorer: Use the bottom panel to input mock recall variables (such as Listeria detection) to calculate real-time threat scores for your supply chain.

👥 Team

Developed by TrustMeBro.

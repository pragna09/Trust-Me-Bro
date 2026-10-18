
# Recall Triage 🚨

### Automated FDA Recall Analysis, Geographic Mapping, and Risk Triage

Recall Triage is an enterprise-grade platform that automates the collection, geographic mapping, and risk analysis of FDA recalls. By analyzing complex recall datasets—such as food contamination from *Listeria*, dangerous allergens, or foreign objects—Recall Triage enables supply chain managers, retailers, and consumers to identify high-priority local threats and act quickly.

## 📸 Key Features

- **Geographic Risk Analysis:** Cross-references FDA distribution data against target regions (e.g., Texas) to assess immediate local impact.
- **Automated Urgency Categorization:** Classifies recalls into actionable urgency levels, such as `Pull now` versus `Monitor`.
- **Interactive Timeline Replay:** Dynamically steps through FDA product recall timelines to observe how risks evolve over time.
- **Regional Breakdown Metrics:** Displays top state-level alerts, keyword accuracy statistics, and distribution coverage.
- **Interactive Risk Scoring Tool:** Accepts new variables (e.g., pathogens, allergens, and affected lots) to calculate custom risk scores and support supplier risk assessments against the database.

## 🛠️ Architecture & Tech Stack

Recall Triage is designed to run on secure, high-performance infrastructure to support the processing of critical public safety data from the [openFDA Food Enforcement API](https://open.fda.gov/apis/food/enforcement/).

- **Backend Environment:** IBM LinuxONE cloud instance for high-performance computing, cryptographic protection, and enterprise security.
- **Backend Processing:** Python 3, isolated using a Python virtual environment.
- **Frontend Interface:** Interactive web dashboard accessible through modern web browsers, including Google Chrome.
- **Version Control:** GitHub — [Trust-Me-Bro/Recall-Triage](https://github.com/Trust-Me-Bro/Recall-Triage).

<img width="6900" height="4380" alt="recall_triage_flowchart" src="https://github.com/user-attachments/assets/6c41e2bd-c4d6-48d6-8bb7-4bf1ecd9d558" />


## 🚀 Getting Started & Local Setup

Follow these steps to connect to the IBM LinuxONE server and access the application through SSH port forwarding.

### Prerequisites

- An SSH private key (`.pem` or equivalent) stored locally.
- Python 3 installed on the remote instance.
- Git installed on the remote instance.
- A modern web browser, such as Google Chrome.
- SSH access to the IBM LinuxONE instance.

### Step 1: Connect to the IBM LinuxONE Server

Open a terminal, navigate to the directory containing your SSH private key, and connect to the remote instance:

```bash
cd ~/Downloads
ssh -i your-private-key.pem user@your-linuxone-ip
```

Replace `your-private-key.pem`, `user`, and `your-linuxone-ip` with your actual credentials and server address.

### Step 2: Clone the Repository and Set Up the Virtual Environment

Once connected to the IBM LinuxONE server, run:

```bash
# Clone the repository
git clone https://github.com/Trust-Me-Bro/Recall-Triage.git
cd Recall-Triage

# Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Start the Application Server

With the virtual environment activated, start the backend application:

```bash
python app.py
```

Keep this terminal session running while using the dashboard.

> **Note:** The application must listen on port `8000` for the port-forwarding command below to work. If the server uses a different port, update the forwarding configuration accordingly.

### Step 4: Access the Dashboard via SSH Port Forwarding

Open a **second terminal window on your local machine** and establish an SSH tunnel that forwards local port `8000` to port `8000` on the remote server:

```bash
ssh -N -L 8000:localhost:8000 \
  -i ~/Downloads/your-private-key.pem \
  user@your-linuxone-ip
```

Keep the SSH tunnel running. Replace the placeholder key path, username, and server address with your actual values.

Open your browser and navigate to:

**http://localhost:8000**

## 📊 Using the Dashboard

- **Timeline Replay:** Click **Restart replay** to step through FDA recall events chronologically.
- **Actionable Urgency Tags:** Review tags such as `Pull now` for high-priority regional threats (e.g., active distribution in Texas) and `Monitor` for lower-priority items.
- **Analytics:** Explore regional breakdown charts, top local alerts, and system accuracy statistics.
- **Interactive Risk Scorer:** Use the scoring panel to enter recall variables, such as *Listeria* detection, and calculate real-time threat scores to support supply chain risk assessment.

## 👥 Team

Developed by **TrustMeBro** - Nishi, Pragna, Ria, Shriya, Tvisha, Vedangi.

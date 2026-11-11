EGYPT AI READINESS — WORKING STREAMLIT PROTOTYPE
=================================================

WHAT THIS PACKAGE CONTAINS
- The uploaded working bilingual survey application, preserved as the base.
- Researcher dashboard addition for the original 27 Google Forms responses.
- A separate tab for new web-app submissions stored in SQLite.
- The original dataset and preliminary reliability summary in /data.
- Existing English/Arabic survey content, scoring, recommendations and PDF reporting.

IMPORTANT DATA SEPARATION
The 27 historical Google Forms responses are displayed from the Excel file in /data.
They are NOT inserted into SQLite and are NOT counted as new app submissions.
Do not combine the datasets unless the supervisor approves a documented procedure.

STEP-BY-STEP — WINDOWS / VS CODE
1. Download and extract this ZIP to a new folder (keep your original folder unchanged).
2. Open VS Code.
3. Select File > Open Folder and choose the extracted project folder.
4. Select Terminal > New Terminal.
5. Confirm the terminal path is the project folder (the folder containing app.py).
6. Create a virtual environment:
   python -m venv .venv
7. Activate it in PowerShell:
   .\.venv\Scripts\Activate.ps1
   If PowerShell blocks activation, run:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   Then activate again.
8. Install packages:
   python -m pip install -r requirements.txt
9. Open .streamlit/secrets.toml in VS Code.
10. Replace CHANGE_ME_BEFORE_RUNNING with a strong private researcher password.
    Do not share it or commit it to GitHub.
11. Save the file.
12. Run:
    python -m streamlit run app.py
13. Open the Local URL printed in the terminal (normally http://localhost:8501).
14. Test the respondent journey before using it: welcome, language, eligibility,
    profile, all five dimensions, submission, results, PDF report.
15. Open Researcher Dashboard in the sidebar and sign in with the password you set.
16. Confirm the two tabs are separate:
    - Original Google Forms (27)
    - New web-app submissions
17. Test CSV export and logout.
18. Delete test submissions from the local database before any approved data collection.

SCORING IN THE PROTOTYPE
- Each dimension contains six Likert items scored 1–5.
- Dimension mean = mean of the six items.
- Dimension score (0–100) = ((dimension mean - 1) / 4) * 100.
- Overall score = unweighted mean of the five dimension scores.
- A dimension score is calculated only when all six items are answered.
- The 0–100 transformation is descriptive; provisional verbal bands are not validated cut-offs.
- The direct overall-readiness answer is shown separately from the calculated composite score.

RESEARCH INTERPRETATION
- The original dataset contains 27 completed responses, not 30.
- It is purposive/non-probability and highly concentrated geographically (26 Cairo, 1 Giza).
- These responses represent respondents' perceptions, not objective audits of agencies.
- Do not claim national representativeness or generalize to all Egyptian public-sector organizations.
- Cronbach's alpha is preliminary internal-consistency evidence, not proof of validity.
- The Public Service and Value dimension combines several related ideas; interpret its score cautiously.

BEFORE REAL OR ONLINE DATA COLLECTION
- Obtain supervisor / GIU ethics approval for the final questionnaire, eligibility rule and consent.
- Confirm privacy notice, data minimization, retention/deletion, access controls and hosting.
- Do not collect sensitive or identifiable government information.
- This is a local prototype, not a security-audited production system.
- SQLite is appropriate for local testing; choose and test secure persistent storage before
  multi-user hosting. Streamlit-hosted local files may not persist reliably across restarts.
- Do not publish the original respondent data, database, secrets or credentials in a public repo.

TROUBLESHOOTING
- If 'streamlit' is not recognized, activate .venv and rerun:
  python -m pip install -r requirements.txt
- If port 8501 is busy:
  python -m streamlit run app.py --server.port 8502
- Stop the app with Ctrl+C in the terminal.

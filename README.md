# GDP Labs Weekly Report Generator

This project automates the generation of weekly reports by fetching data from GitHub, SonarQube, Google Calendar, and using AI to summarize accomplishments. It also creates draft emails in Gmail.

## Setup

1. Clone this repository
2. Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This script will:

- Create a virtual environment
- Install required dependencies
- Create a `.env` file from `.env.example`

3. Set up your environment variables (see below)

## Environment Variables

Edit the `.env` file created by the setup script and fill in the following variables:

### GITHUB_PERSONAL_ACCESS_TOKEN

- Get from: <https://github.com/settings/tokens/new>
- Use "Personal Access Token (Classic)"
- Required scopes: `repo`

### GITHUB_USERNAME

- Your GitHub username

### GOOGLE_CLIENT_SECRET_FILE

1. Create a new Google Cloud project: <https://console.cloud.google.com/projectcreate>
2. Enable the Google Calendar API: <https://console.cloud.google.com/apis/library/calendar-json.googleapis.com>
3. Create an OAuth client ID credential:
   - Go to: <https://console.cloud.google.com/apis/credentials>
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - In the OAuth client creation process, you'll need to configure the consent screen
   - When asked about scopes, add: 
     - `https://www.googleapis.com/auth/calendar.readonly`
     - `https://www.googleapis.com/auth/gmail.compose`
4. After creating the OAuth client ID, go to the OAuth consent screen page: <https://console.cloud.google.com/apis/credentials/consent>
   - Add a test user with your GDP Labs email (@gdplabs.id)
5. Download the JSON credentials file and place it in the root directory of this project
6. Fill this env variable with the filename of the credentials file
   (e.g., if your file is named `client_secret_XXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXX.apps.googleusercontent.com.json`,
   you would enter that exact filename)

### GOOGLE_GEMINI_API_KEY

- Get from: <https://aistudio.google.com/app/apikey>

### GROQ_API_KEY

- Get from: <https://console.groq.com/keys>

### REPO_NAME

- The name of the GitHub repository you're reporting on, e.g. `CATAPA-API`

### REPO_OWNER

- Set to: `GDP-ADMIN`

### SONARQUBE_USER_TOKEN

- Get from: <https://sqa.gdplabs.net/account/security>
- Use the "User Token" option

## Gmail API Setup

To set up the Gmail API for creating draft emails:

1. Go to the Google Cloud Console: <https://console.cloud.google.com/>
2. Select your project
3. Navigate to "APIs & Services" > "Library"
4. Search for "Gmail API" and click on it
5. Click "Enable" to enable the Gmail API for your project
6. If prompted, create credentials (OAuth client ID) for the Gmail API
   - Choose "Desktop app" as the application type
   - Download the client configuration and save it as described in the GOOGLE_CLIENT_SECRET_FILE section
7. Ensure that the `https://www.googleapis.com/auth/gmail.compose` scope is included in your OAuth consent screen

## Usage

After setting up your environment variables, you can run the script using:

```bash
python3 main.py
```

or you can try out generating reports with AI Agents using:

```bash
python3 agent_main.py
```

This script will:

1. Collect and preprocess data from various sources
2. Generate a weekly report using AI agents
3. Allow for user feedback and refinement of the report
4. Save the final report in the `output` directory
5. Create a draft email in Gmail

## Customization

- Modify `user_input.py` to add custom input for your weekly reports
- Adjust the report template in `TEMPLATE.md` to change the structure of your reports

## Project Structure

- `main.py`: Main entry point for the report generation process
- `data_collector.py`: Handles data collection from various sources
- `data_preprocessor.py`: Preprocesses the collected data
- `agent_creator.py`: Creates AI agents and tasks for report generation
- `report_generator.py`: Generates the report and handles user feedback
- `api_utils.py`: Utilities for interacting with Gmail API

## Troubleshooting

If you encounter any issues with authentication or API access:

1. Double-check your environment variables
2. Ensure you have the necessary permissions for each service
3. For Google APIs (Calendar, Gmail), you may need to authorize the application on first run. Follow the prompts in the console to complete the OAuth flow.
4. If you encounter scope-related errors, make sure all required scopes are included in your OAuth consent screen configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
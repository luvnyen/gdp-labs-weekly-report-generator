# GDP Labs Weekly Report Generator

This project automates the generation of weekly reports by fetching data from GitHub, SonarQube, and Google Calendar, and using AI to summarize accomplishments.

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
   - When asked about scopes, add: `https://www.googleapis.com/auth/calendar.readonly`
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

## Usage

After setting up your environment variables, you can run the script using:

```bash
./run.sh
```

This script will:

1. Activate the virtual environment
2. Run the weekly report generator
3. Generate a report in the `output` directory and save the raw accomplishments data in `ACCOMPLISHMENTS_RAW.md`

## Customization

- Modify `user_input.py` to add custom input for your weekly reports
- Adjust the report template in `TEMPLATE.md` to change the structure of your reports

## Troubleshooting

If you encounter any issues with authentication or API access, double-check your environment variables and ensure you have the necessary permissions for each service.

For Google Calendar integration, you may need to authorize the application on first run. Follow the prompts in the console to complete the OAuth flow.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

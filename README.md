# 🚧 UNDER CONSTRUCTION 🚧

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

3. Set up your environment variables

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

- Modify `user_data.py` to add custom input for your weekly reports
- Adjust the report template in `/templates/template.md` to change the structure of your reports

## Troubleshooting

If you encounter any issues with authentication or API access, double-check your environment variables and ensure you have the necessary permissions for each service.

For Google Calendar integration, you may need to authorize the application on first run. Follow the prompts in the console to complete the OAuth flow.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

# Gmail Rule Processor

## Overview
The Gmail Rule Processor is a Python-based application that processes emails from a Gmail account based on predefined rules. The application utilizes the Gmail API for fetching emails, applies rule-based operations, and performs actions such as marking emails as read/unread and moving messages to different labels.

## Features
- Authenticate with Gmail using OAuth 2.0
- Fetch emails and store them in a relational database
- Apply rules from a JSON configuration file
- Perform automated actions like marking emails as read/unread or moving emails
- Logging and error handling for smooth operation

## Technologies Used
- **Python**
- **Gmail API** (for email processing)
- **SQLite** (for storing emails and rules)
- **OAuth 2.0** (for secure authentication)

## Installation

### Prerequisites
- Install Python 3.13 from [Python's official website](https://www.python.org/downloads/) or using Homebrew on macOS:
  ```sh
  brew install python
  ```
- Install `pip` if not already installed (comes with Python)
- Install `virtualenv` using:
  ```sh
  pip install virtualenv
  ```
- Create a Google Cloud Project and enable Gmail API
- Generate OAuth 2.0 credentials

### Generating `credentials.json`
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services > Library**
4. Enable the **Gmail API**
5. Go to **APIs & Services > Credentials**
6. Click **Create Credentials** and select **OAuth client ID**
7. Configure the consent screen and choose **Desktop App**
8. Download the `credentials.json` file and place it in the project root directory

### Setting Up Virtual Environment
1. Clone the repository:
   ```sh
   git clone https://github.com/Poornima2212/gmail_rule_processor.git
   cd gmail-rule-processor
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the Application
Run the application using:
   ```sh
   python3 authenticate.py
   python3 fetch_emails.py
   python3 apply_rules.py

   ```

## Usage
- The application will fetch emails and process them based on the rules defined in `rules.json`.
- Logs and processed results can be found in the output console.

## Testing
Run unit tests using:
```sh
pytest
```

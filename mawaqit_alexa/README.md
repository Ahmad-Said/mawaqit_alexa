# Mawaqit to Alexa

This project allows Alexa to announce notifications for each prayer 15 minutes before and at the time of the prayer.

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

This project aims to integrate Mawaqit prayer times with Alexa through Microsoft Outlook. By generating a calendar file from Mawaqit and importing it into Outlook, Alexa can be linked to the Outlook calendar to announce prayer times.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have python installed
- You have Microsoft Outlook installed and configured.
- You have an Amazon Alexa device.

## Installation

1. Clone the repository to your local machine:

    ```sh
    git clone https://github.com/Ahmad-Said/mawaqit-to-alexa.git
    cd mawaqit-to-alexa
    ```

2. Install the necessary dependencies. This project requires Python and several Python packages. You can install them using pip:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

Follow these steps to generate the calendar file and link it to Alexa:

1. **Provide Mawaqit URL:**

    In the `main.py` file, provide the URL of your Mawaqit calendar. The URL should look something like this:
    
    ```python
    data_url = "https://mawaqit.net/en/your-mosque-url"
    ```

2. **Run the script to generate the calendar file:**

    Execute the main function in the script to download the prayer times and generate the calendar file:

    ```sh
    python main.py
    ```

    This will generate a calendar file in out directory (e.g., `out/prayer_times.ics`) in the project directory.


3. **Import the calendar into Microsoft Outlook:**
    - See [doc/to_alexa](../doc/to_alexa) for the rest of tuto
    - Open Microsoft Outlook.
    - Go to `File` > `Open & Export` > `Import/Export`.
    - Select `Import an iCalendar (.ics)` and click `Next`.
    - Locate and select the generated `prayer_times.ics` file and import it.

4. **Link Alexa with Outlook Calendar:**

    - Open the Alexa app on your phone.
    - Go to `Settings` > `Calendar & Email`.
    - Select `Microsoft Outlook` and sign in with your Outlook account.
    - Ensure the calendar is linked and Alexa has permission to access it.

5. **Configure Alexa to Announce Events:**

    - In the Alexa app, go to `Settings` > `Notifications` > `Calendar`.
    - Ensure `Announce Event Notifications` is enabled.

Alexa will now announce notifications for each prayer 15 minutes before and at the time of the prayer.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

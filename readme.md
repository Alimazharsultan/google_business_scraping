## Documentation for Running the Google Business Scraper

### Overview
The Google Business Scraper can be run either via the `gui_scraper.exe` executable or by using the `gui_scraper.py` Python script. Below are detailed instructions for both methods, as well as information on how to install the required Playwright binaries.

---

### Option 1: Running the Scraper via the Executable (`gui_scraper.exe`)

#### Requirements
- **Operating System**: Windows
- **Pre-installed Libraries**: None required (all dependencies are bundled in the executable)

#### Steps
1. **Locate the Executable**: Navigate to the `dist/` folder where the `gui_scraper.exe` is located.
   - Path: `dist/gui_scraper.exe`
   
2. **Run the Executable**:
   - Double-click `gui_scraper.exe` to launch the GUI for the scraper.
   
3. **Enter Inputs**:
   - **CSV File**: Browse and select the CSV file (e.g., `uscities.csv`).
   - **Cities to Scrape**: Enter the number of cities you want to scrape.
   - **Pages to Scroll**: Enter the number of pages to scroll.
   - **Professions**: Enter one profession per line.
   - **Show browser while scraping**: Tick the checkbox if you want the scraper to run showing a browser window.
   - **Include HTML in Output**: Tick the checkbox if you want to include HTML code in the output file.
   
4. **Run Scraper**: Click the "Run Scraper" button. The logs and output will be displayed in the text box at the bottom of the GUI.

---

### Option 2: Running the Scraper via Python (`gui_scraper.py`)

#### Requirements
- **Operating System**: Any OS with Python installed (e.g., Windows, MacOS, Linux)
- **Python Version**: Python 3.7 or higher
- **Libraries**: Playwright, Tkinter (comes pre-installed with Python), CSV, and other built-in modules

#### Steps

1. **Install Dependencies**:
   - Open a terminal or command prompt and navigate to the project folder.
   - Install the required Python libraries:
     ```bash
     pip install -r requirements.txt
     ```

2. **Install Playwright Binaries**:
   Playwright requires additional browser binaries for automation. To install them:
   ```bash
   playwright install
   ```

3. **Run the Script**:
   - To run the scraper, use the following command:
     ```bash
     python gui_scraper.py
     ```

4. **Enter Inputs in the GUI**:
   - Provide the same inputs as mentioned in the executable section:
     - **CSV File**: Browse and select `uscities.csv`.
     - **Cities to Scrape**: Enter a number.
     - **Pages to Scroll**: Enter a number.
     - **Professions**: Add one profession per line.
     - **Headless Mode** and **HTML Output**: Check/uncheck the boxes based on your needs.
   
5. **Run Scraper**: Click the "Run Scraper" button to start the process.

---

### Troubleshooting & Notes

- **Playwright Installation**:
  - If you encounter any issues with Playwright, ensure that the browser binaries are installed correctly by running:
    ```bash
    playwright install
    ```
  
- **Log Output**: 
  - All print statements during the scraping process will be displayed in the GUI for both methods.

- **Output**:
  - The results will be saved in the `output` folder. The file format and content will depend on the options selected (CSV or text file with HTML).

This documentation provides a comprehensive guide for both technical and non-technical users to run the scraper effectively.
# Python Weather.com Deployment Manual

## Deployment Environment
- **Windows Version:** 10
- **Python Version:** 3.7
- **PyCharm Version:** 2021.3
- **MongoDB Version:** 4.0

## Deployment Process
### Step 1: Install Dependencies
First, install the required Python packages using pip:

```bash
pip install -r WeatherAnalysic/requirement.txt
```

### Step 2: Crawler/Model Module
Run the weather spider script to fetch and process weather data:

```bash
python WeatherAnalysic/spider/weatherSpider.py
```

### Step 3: Backend Server
Start the backend server by running the `app.py` script:

```bash
python WeatherAnalysic/app.py
```

### Step 4: Frontend Setup
Finally, to view the frontend interface, open `demo.html` in a web browser.

## Notes
- Ensure that MongoDB is properly installed and running on your system.
- Make sure all the paths and file names are correct and correspond to your project's structure.
- Check if the ports specified in the application do not conflict with other services on your system.
- This README provides a clear and concise guide for setting up and running the Python weather application on a Windows environment with the specified software versions.

# Grade Calculator

A modern, interactive Grade Calculator application built with Python and [Flet](https://flet.dev/).

## Features

*   **Calculate GPA**: Enter course names, credits, and grades to calculate your semester GPA.
*   **Save Semesters**: Save your semester data to keep track of your academic progress.
*   **Year Categorization**: Organize your semesters by year (Year 1, Year 2, etc.).
*   **Cumulative GPA**: Automatically calculates your cumulative GPA across all saved semesters.
*   **Visual Dashboard**: Visualize your academic performance with interactive charts.
    *   **GPA Trend**: View your GPA progression over time using a line chart.
    *   **Grade Distribution**: See a breakdown of your grades in a pie chart.
    *   **Download Charts**: Save your charts as images.
*   **Dark/Light Theme**: Toggle between dark and light modes. Your preference is saved automatically.
*   **Edit & Delete**: Easily edit or delete previously saved semesters.
*   **Import Data**: Quickly import course data from text.
*   **Data Persistence**: Your data is saved locally (`grade_data.json`), so it`s there when you come back.
*   **Responsive UI**: Clean and responsive user interface.

## Prerequisites

*   Python 3.7 or higher

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Yotshiba/grade_callculater_or_simulator.git
    cd grade_callculater_or_simulator
    ```

2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the application:

```bash
python main.py
```

## Project Structure

The project is organized as follows:

```
Grade_calculator/
│   main.py                  # Entry point of the application
│   grade_data.json          # Data file for saved grades
│   settings.json            # Settings file (theme preference)
│   README.md                # Project documentation
│
└───grade_calculator_app/    # Application package
        __init__.py
        models.py            # Data models (Course, Semester, GradeManager)
        data_manager.py      # Handles loading/saving data and settings
        ui.py                # UI components and logic
```

## How to Use

### Calculator Tab
1.  **Import Data** (Optional): Click "Import" and paste your course data to automatically fill the form.
2.  **Add Courses**: Click "Add Course" to add more rows.
3.  **Enter Details**: Fill in the Course Name, Credits, and select a Grade.
4.  **Calculate**: Click "Calculate GPA" to see the GPA for the current entries.
5.  **Save**:
    *   Select the **Year**.
    *   Enter a **Semester Name** (e.g., "Semester 1").
    *   Click "Save Semester".
6.  **Manage History**:
    *   View your history at the bottom, grouped by year.
    *   Click the **Pencil icon** to edit a semester.
    *   Click the **Trash icon** to delete a semester.
    *   Click "Clear History" to delete all saved data.

### Dashboard Tab
1.  Switch to the **Dashboard** tab at the top of the application.
2.  **Filter by Year**: Use the dropdown to view statistics for "All Years" or a specific year.
3.  **View Charts**:
    *   **GPA Summary**: A line chart showing your GPA trend across semesters/years.
    *   **Grade Distribution**: A pie chart showing the distribution of your letter grades.
4.  **Download**: Click the "Download Chart" button to save the current view as an image.

## License

[MIT](LICENSE)


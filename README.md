# Grade Calculator

A modern, interactive Grade Calculator application built with Python and [Flet](https://flet.dev/).

## Features

*   **Calculate GPA**: Enter course names, credits, and grades to calculate your semester GPA.
*   **Save Semesters**: Save your semester data to keep track of your academic progress.
*   **Year Categorization**: Organize your semesters by year (Year 1, Year 2, etc.).
*   **Cumulative GPA**: Automatically calculates your cumulative GPA across all saved semesters.
*   **Edit & Delete**: Easily edit or delete previously saved semesters.
*   **Import Data**: Quickly import course data from text.
*   **Data Persistence**: Your data is saved locally (`grade_data.json`), so it's there when you come back.
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
    pip install flet
    ```

## Usage

Run the application:

```bash
python grade_calculator.py
```

## How to Use

1.  **Import Data** (Optional): Click "Import" and paste your course data to automatically fill the form.
2.  **Add Courses**: Click "Add Course" to add more rows.
3.  **Enter Details**: Fill in the Course Name, Credits, and select a Grade.
4.  **Calculate**: Click "Calculate GPA" to see the GPA for the current entries.
4.  **Save**:
    *   Select the **Year**.
    *   Enter a **Semester Name** (e.g., "Semester 1").
    *   Click "Save Semester".
5.  **Manage History**:
    *   View your history at the bottom, grouped by year.
    *   Click the **Pencil icon** to edit a semester.
    *   Click the **Trash icon** to delete a semester.
    *   Click "Clear History" to delete all saved data.

## License

[MIT](LICENSE)

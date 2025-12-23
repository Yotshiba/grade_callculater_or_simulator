import flet as ft
import json
import os

def main(page: ft.Page):
    page.title = "Grade Calculator"
    page.window_width = 800
    page.window_height = 700
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT

    DATA_FILE = "grade_data.json"

    grade_values = {
        "A": 4.0,
        "B+": 3.5,
        "B": 3.0,
        "C+": 2.5,
        "C": 2.0,
        "D+": 1.5,
        "D": 1.0,
        "F": 0.0
    }

    # Data structure:
    # saved_data = {
    #   "Year 1": [ {semester_obj}, ... ],
    #   "Year 2": [ ... ]
    # }
    saved_data = {}

    # UI Elements
    course_rows = ft.Column(spacing=10)
    result_text = ft.Text("GPA: 0.00", size=24, weight="bold", color=ft.Colors.BLUE)
    
    semester_name_field = ft.TextField(label="Semester Name", value="Semester 1", width=200)
    year_dropdown = ft.Dropdown(
        label="Year",
        width=150,
        options=[
            ft.dropdown.Option("Year 1"),
            ft.dropdown.Option("Year 2"),
            ft.dropdown.Option("Year 3"),
            ft.dropdown.Option("Year 4"),
            ft.dropdown.Option("Other"),
        ],
        value="Year 1"
    )

    history_column = ft.Column(spacing=10)
    cumulative_result_text = ft.Text("Cumulative GPA: 0.00", size=20, weight="bold", color=ft.Colors.GREEN)

    # --- Helper Functions ---

    def save_to_file():
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(saved_data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_from_file():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    # Migrate old list format to new dict format if necessary
                    if isinstance(data, list):
                        saved_data.clear()
                        saved_data["Year 1"] = data
                    else:
                        saved_data.update(data)
                    refresh_history_view()
                    update_cumulative_gpa()
            except Exception as e:
                print(f"Error loading data: {e}")

    def get_current_semester_data():
        total_points = 0
        total_credits = 0
        courses = []
        
        for row in course_rows.controls:
            name_field = row.controls[0]
            credit_field = row.controls[1]
            grade_dropdown = row.controls[2]
            
            try:
                if not credit_field.value or not grade_dropdown.value:
                    continue

                credits = float(credit_field.value)
                grade = grade_dropdown.value
                name = name_field.value
                
                if grade in grade_values:
                    points = grade_values[grade]
                    total_points += points * credits
                    total_credits += credits
                    
                    courses.append({
                        "name": name,
                        "credits": credits,
                        "grade": grade
                    })
            except (ValueError, TypeError):
                continue 
        
        return total_points, total_credits, courses

    def calculate_gpa(e):
        total_points, total_credits, _ = get_current_semester_data()
        
        if total_credits > 0:
            gpa = total_points / total_credits
            result_text.value = f"GPA: {gpa:.2f}"
        else:
            result_text.value = "GPA: 0.00"
        
        page.update()

    def update_cumulative_gpa():
        cum_points = 0
        cum_credits = 0
        
        for year, semesters in saved_data.items():
            for s in semesters:
                cum_points += s.get('points', 0)
                cum_credits += s.get('credits', 0)
        
        if cum_credits > 0:
            cgpa = cum_points / cum_credits
            cumulative_result_text.value = f"Cumulative GPA: {cgpa:.2f}"
        else:
            cumulative_result_text.value = "Cumulative GPA: 0.00"

    def save_semester(e):
        total_points, total_credits, courses = get_current_semester_data()
        
        if total_credits == 0:
            page.snack_bar = ft.SnackBar(ft.Text("Cannot save empty semester!"))
            page.snack_bar.open = True
            page.update()
            return

        gpa = total_points / total_credits
        sem_name = semester_name_field.value
        year = year_dropdown.value
        
        semester_data = {
            'name': sem_name,
            'points': total_points,
            'credits': total_credits,
            'gpa': gpa,
            'courses': courses
        }
        
        if year not in saved_data:
            saved_data[year] = []
            
        # Check if updating existing semester (simple check by name for now, could be improved with IDs)
        # For now, we just append. Editing is handled by "Edit" button in history.
        saved_data[year].append(semester_data)
        
        save_to_file()
        refresh_history_view()
        update_cumulative_gpa()
        
        # Reset form
        clear_all(None)
        page.snack_bar = ft.SnackBar(ft.Text(f"Saved {sem_name} to {year}"))
        page.snack_bar.open = True
        page.update()

    def edit_semester(year, index):
        semester = saved_data[year][index]
        
        # Load data back into form
        semester_name_field.value = semester['name']
        year_dropdown.value = year
        
        course_rows.controls.clear()
        for course in semester.get('courses', []):
            row = create_course_row()
            row.controls[0].value = course['name']
            row.controls[1].value = str(course['credits'])
            row.controls[2].value = course['grade']
            course_rows.controls.append(row)
            
        # Remove from saved data so it can be re-saved
        del saved_data[year][index]
        if not saved_data[year]:
            del saved_data[year]
            
        save_to_file()
        refresh_history_view()
        update_cumulative_gpa()
        calculate_gpa(None)
        page.update()

    def delete_semester(year, index):
        del saved_data[year][index]
        if not saved_data[year]:
            del saved_data[year]
        save_to_file()
        refresh_history_view()
        update_cumulative_gpa()
        page.update()

    def refresh_history_view():
        history_column.controls.clear()
        
        # Sort years
        sorted_years = sorted(saved_data.keys())
        
        for year in sorted_years:
            semesters = saved_data[year]
            
            year_semesters_column = ft.Column(spacing=5)
            
            for i, semester in enumerate(semesters):
                # Capture current values for closure
                current_year = year
                current_index = i
                
                year_semesters_column.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column([
                                    ft.Text(semester['name'], weight="bold"),
                                    ft.Text(f"Credits: {semester['credits']:.1f} | GPA: {semester['gpa']:.2f}", size=12, color=ft.Colors.GREY_700),
                                ]),
                                ft.Row([
                                    ft.IconButton(ft.Icons.EDIT, icon_color="blue", tooltip="Edit", on_click=lambda e, y=current_year, idx=current_index: edit_semester(y, idx)),
                                    ft.IconButton(ft.Icons.DELETE, icon_color="red", tooltip="Delete", on_click=lambda e, y=current_year, idx=current_index: delete_semester(y, idx)),
                                ])
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=10,
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=5
                    )
                )
            
            history_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(year, size=16, weight="bold", color=ft.Colors.INDIGO),
                        year_semesters_column
                    ]),
                    padding=ft.padding.only(bottom=10)
                )
            )
        page.update()

    def create_course_row():
        row = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
        
        def delete_row(e):
            course_rows.controls.remove(row)
            page.update()

        name_field = ft.TextField(label="Course Name", expand=3, text_size=14, content_padding=10)
        credit_field = ft.TextField(label="Credits", expand=1, text_size=14, content_padding=10, keyboard_type=ft.KeyboardType.NUMBER)
        grade_dropdown = ft.Dropdown(
            expand=1,
            label="Grade",
            text_size=14,
            content_padding=10,
            options=[ft.dropdown.Option(g) for g in grade_values.keys()]
        )
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color="red",
            on_click=delete_row
        )

        row.controls = [name_field, credit_field, grade_dropdown, delete_btn]
        return row

    def add_course_row(e=None):
        course_rows.controls.append(create_course_row())
        page.update()

    def clear_all(e):
        course_rows.controls.clear()
        result_text.value = "GPA: 0.00"
        semester_name_field.value = "Semester 1"
        # Add 4 initial rows back
        for _ in range(4):
            add_course_row()
        page.update()

    def clear_history(e):
        saved_data.clear()
        save_to_file()
        refresh_history_view()
        update_cumulative_gpa()
        page.update()

    # --- Import Dialog ---
    import_text_field = ft.TextField(
        multiline=True,
        min_lines=10,
        max_lines=15,
        label="Paste your course data here",
        hint_text="01999021\n3 หน่วยกิต\nThai Name\n\nEnglish Name\nGrade\n..."
    )

    def close_import_dialog(e):
        page.close(import_dialog)

    def run_import(e):
        text = import_text_field.value
        if not text:
            close_import_dialog(None)
            return

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Clear existing rows
        course_rows.controls.clear()
        
        i = 0
        while i < len(lines):
            # We expect chunks of 5 lines (ignoring empty lines)
            # 0: Code
            # 1: Credits (contains "หน่วยกิต")
            # 2: Name TH
            # 3: Name EN
            # 4: Grade
            
            if i + 4 >= len(lines):
                break
                
            code = lines[i]
            credits_str = lines[i+1]
            name_th = lines[i+2]
            name_en = lines[i+3]
            grade = lines[i+4]
            
            # Basic validation to ensure we are aligned
            if "หน่วยกิต" not in credits_str:
                # Try to recover or skip
                i += 1
                continue

            try:
                credits = float(credits_str.split()[0])
            except:
                credits = 0.0

            row = create_course_row()
            # Set Name (Code + English Name)
            row.controls[0].value = f"{code} {name_en}"
            # Set Credits
            row.controls[1].value = str(credits)
            # Set Grade
            if grade in grade_values:
                row.controls[2].value = grade
            else:
                # If grade is not in our list (e.g. "N"), leave it empty
                row.controls[2].value = None

            course_rows.controls.append(row)
            i += 5
        
        import_text_field.value = ""
        close_import_dialog(None)
        page.snack_bar = ft.SnackBar(ft.Text("Data imported successfully!"))
        page.snack_bar.open = True
        page.update()

    import_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Import Data"),
        content=import_text_field,
        actions=[
            ft.TextButton("Cancel", on_click=close_import_dialog),
            ft.TextButton("Import", on_click=run_import),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_import_dialog(e):
        page.open(import_dialog)

    # Buttons
    add_btn = ft.ElevatedButton("Add Course", icon=ft.Icons.ADD, on_click=add_course_row)
    import_btn = ft.ElevatedButton("Import", icon=ft.Icons.UPLOAD_FILE, on_click=open_import_dialog)
    calc_btn = ft.ElevatedButton("Calculate GPA", icon=ft.Icons.CALCULATE, on_click=calculate_gpa)
    save_btn = ft.ElevatedButton("Save Semester", icon=ft.Icons.SAVE, on_click=save_semester, color="green")
    clear_btn = ft.ElevatedButton("Clear Form", icon=ft.Icons.CLEAR_ALL, on_click=clear_all, color="red")
    clear_hist_btn = ft.ElevatedButton("Clear History", icon=ft.Icons.DELETE_FOREVER, on_click=clear_history, color="red")

    # Header
    header = ft.Row(
        controls=[
            ft.Container(content=ft.Text("Course Name", weight="bold", text_align="center"), expand=3, alignment=ft.alignment.center),
            ft.Container(content=ft.Text("Credits", weight="bold", text_align="center"), expand=1, alignment=ft.alignment.center),
            ft.Container(content=ft.Text("Grade", weight="bold", text_align="center"), expand=1, alignment=ft.alignment.center),
            ft.Container(width=40) # Spacer for delete button
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # Layout
    page.add(
        ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Grade Calculator", size=30, weight="bold"),
                    alignment=ft.alignment.center,
                    padding=20
                ),
                # Semester Info Inputs
                ft.Row([
                    year_dropdown,
                    semester_name_field
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Row([add_btn, import_btn, calc_btn, save_btn, clear_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                header,
                course_rows,
                ft.Divider(),
                ft.Container(
                    content=result_text,
                    alignment=ft.alignment.center,
                    padding=10
                ),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Text("Semester History", size=20, weight="bold"),
                        clear_hist_btn
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                history_column,
                ft.Container(
                    content=cumulative_result_text,
                    alignment=ft.alignment.center,
                    padding=20
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )
    )

    # Load saved data
    load_from_file()

    # Add initial rows
    for _ in range(4):
        add_course_row()

if __name__ == "__main__":
    ft.app(target=main)

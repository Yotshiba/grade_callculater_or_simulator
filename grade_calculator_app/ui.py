import flet as ft
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from .models import GradeManager, Semester, Course
from .data_manager import DataManager

matplotlib.use('Agg')

class GradeCalculatorUI:
    def __init__(self, page: ft.Page, data_manager: DataManager):
        self.page = page
        self.data_manager = data_manager
        self.grade_manager = GradeManager()
        
        # Load initial data
        data = self.data_manager.load_data()
        self.grade_manager.load_data(data)

        self.setup_page()
        self.init_state()
        self.build_ui()

    def setup_page(self):
        self.page.title = "Grade Calculator"
        self.page.window_width = 800
        self.page.window_height = 700
        self.page.scroll = "auto"
        
        # Load settings
        self.settings = self.data_manager.load_settings()
        theme_mode = self.settings.get("theme_mode", "light")
        self.page.theme_mode = ft.ThemeMode.DARK if theme_mode == "dark" else ft.ThemeMode.LIGHT

        # Add AppBar with theme toggle
        self.page.appbar = ft.AppBar(
            title=ft.Text("Grade Calculator"),
            center_title=True,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE,
                    on_click=self.toggle_theme,
                    tooltip="Toggle Theme"
                )
            ]
        )

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            e.control.icon = ft.Icons.LIGHT_MODE
            self.settings["theme_mode"] = "dark"
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            e.control.icon = ft.Icons.DARK_MODE
            self.settings["theme_mode"] = "light"
        
        self.data_manager.save_settings(self.settings)
        self.page.update()

    def init_state(self):
        self.editing_state = {
            "is_editing": False,
            "year": None,
            "index": None
        }

    def build_ui(self):
        # --- Calculator Tab Components ---
        self.course_rows = ft.Column(spacing=10)
        self.result_text = ft.Text("GPA: 0.00", size=24, weight="bold", color=ft.Colors.BLUE)
        
        self.semester_name_field = ft.TextField(label="Semester Name", value="Semester 1", width=200)
        self.year_dropdown = ft.Dropdown(
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

        self.history_column = ft.Column(spacing=10)
        self.cumulative_result_text = ft.Text("Cumulative GPA: 0.00", size=20, weight="bold", color=ft.Colors.GREEN)

        # Buttons
        self.add_course_btn = ft.ElevatedButton("Add Course", icon=ft.Icons.ADD, on_click=self.add_course_field)
        self.import_btn = ft.ElevatedButton("Import", icon=ft.Icons.UPLOAD_FILE, on_click=self.open_import_dialog)
        self.calculate_btn = ft.ElevatedButton("Calculate GPA", icon=ft.Icons.CALCULATE, on_click=self.calculate_gpa_handler)
        self.save_btn = ft.ElevatedButton("Save Semester", icon=ft.Icons.SAVE, on_click=self.save_semester_handler)
        self.clear_btn = ft.OutlinedButton("Clear All", icon=ft.Icons.CLEAR_ALL, on_click=self.clear_all)
        self.clear_hist_btn = ft.ElevatedButton("Clear History", icon=ft.Icons.DELETE_FOREVER, on_click=self.clear_history, color="red")

        # Import Dialog
        self.import_text_field = ft.TextField(
            multiline=True,
            min_lines=10,
            max_lines=15,
            label="Paste your course data here",
            hint_text="01999021\n3 หน่วยกิต\nThai Name\n\nEnglish Name\nGrade\n..."
        )
        self.import_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Import Data"),
            content=self.import_text_field,
            actions=[
                ft.TextButton("Cancel", on_click=self.close_import_dialog),
                ft.TextButton("Import", on_click=self.run_import),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Calculator View Layout
        calculator_view = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Grade Calculator", size=30, weight="bold"),
                    alignment=ft.alignment.center,
                    padding=20
                ),
                ft.Row([
                    self.year_dropdown,
                    self.semester_name_field
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Row([self.add_course_btn, self.import_btn, self.calculate_btn, self.save_btn, self.clear_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Container(content=ft.Text("Course Name", weight="bold", text_align="center"), expand=3, alignment=ft.alignment.center),
                        ft.Container(content=ft.Text("Credits", weight="bold", text_align="center"), expand=1, alignment=ft.alignment.center),
                        ft.Container(content=ft.Text("Grade", weight="bold", text_align="center"), expand=1, alignment=ft.alignment.center),
                        ft.Container(width=40) # Spacer for delete button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                self.course_rows,
                ft.Divider(),
                ft.Container(
                    content=self.result_text,
                    alignment=ft.alignment.center,
                    padding=10
                ),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Text("Semester History", size=20, weight="bold"),
                        self.clear_hist_btn
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                self.history_column,
                ft.Container(
                    content=self.cumulative_result_text,
                    alignment=ft.alignment.center,
                    padding=20
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )

        # --- Dashboard Tab Components ---
        self.dashboard_image = ft.Image(src_base64="", width=700, height=500, fit=ft.ImageFit.CONTAIN)
        self.dashboard_year_dropdown = ft.Dropdown(
            label="Filter by Year",
            width=200,
            options=[ft.dropdown.Option("All Years")] + [ft.dropdown.Option(f"Year {i}") for i in range(1, 5)] + [ft.dropdown.Option("Other")],
            value="All Years",
            on_change=self.generate_charts
        )

        dashboard_view = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Dashboard", size=30, weight="bold"),
                    alignment=ft.alignment.center,
                    padding=20
                ),
                ft.Row([
                    self.dashboard_year_dropdown,
                    ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=self.generate_charts),
                    ft.ElevatedButton("Download Chart", icon=ft.Icons.DOWNLOAD, on_click=self.download_chart)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Container(
                    content=self.dashboard_image,
                    alignment=ft.alignment.center
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )

        # --- Main Tabs ---
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Calculator",
                    icon=ft.Icons.CALCULATE,
                    content=calculator_view
                ),
                ft.Tab(
                    text="Dashboard",
                    icon=ft.Icons.DASHBOARD,
                    content=dashboard_view
                ),
            ],
            expand=1,
            on_change=lambda e: self.generate_charts(None) if e.control.selected_index == 1 else None
        )

        self.page.add(self.tabs)

        # Initial setup
        self.add_course_field(None)
        self.add_course_field(None)
        self.add_course_field(None)
        self.add_course_field(None)
        self.refresh_history_view()
        self.update_cumulative_gpa_display()

    # --- Calculator Methods ---

    def create_course_row(self):
        row = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
        
        def delete_row(e):
            self.course_rows.controls.remove(row)
            self.page.update()

        name_field = ft.TextField(label="Course Name", expand=3, text_size=14, content_padding=10)
        credit_field = ft.TextField(label="Credits", expand=1, text_size=14, content_padding=10, keyboard_type=ft.KeyboardType.NUMBER)
        grade_dropdown = ft.Dropdown(
            expand=1,
            label="Grade",
            text_size=14,
            content_padding=10,
            options=[ft.dropdown.Option(g) for g in Course.GRADE_VALUES.keys()]
        )
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color="red",
            on_click=delete_row
        )

        row.controls = [name_field, credit_field, grade_dropdown, delete_btn]
        return row

    def add_course_field(self, e):
        self.course_rows.controls.append(self.create_course_row())
        self.page.update()

    def get_current_semester_from_ui(self):
        sem_name = self.semester_name_field.value
        year = self.year_dropdown.value
        semester = Semester(sem_name, year)
        
        for row in self.course_rows.controls:
            name_field = row.controls[0]
            credit_field = row.controls[1]
            grade_dropdown = row.controls[2]
            
            try:
                if not credit_field.value or not grade_dropdown.value:
                    continue

                credits = float(credit_field.value)
                grade = grade_dropdown.value
                name = name_field.value
                
                semester.add_course(Course(name, credits, grade))
            except (ValueError, TypeError):
                continue 
        
        return semester

    def calculate_gpa_handler(self, e):
        semester = self.get_current_semester_from_ui()
        gpa, _, total_credits = semester.calculate_stats()
        
        if total_credits > 0:
            self.result_text.value = f"GPA: {gpa:.2f}"
        else:
            self.result_text.value = "GPA: 0.00"
        
        self.page.update()

    def save_semester_handler(self, e):
        semester = self.get_current_semester_from_ui()
        _, _, total_credits = semester.calculate_stats()
        
        if total_credits == 0:
            self.page.snack_bar = ft.SnackBar(ft.Text("Cannot save empty semester!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        if self.editing_state["is_editing"]:
            self.grade_manager.update_semester(
                semester, 
                self.editing_state["year"], 
                self.editing_state["index"]
            )
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Updated {semester.name} in {semester.year}"))
        else:
            self.grade_manager.add_semester(semester)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Saved {semester.name} to {semester.year}"))
        
        self.data_manager.save_data(self.grade_manager.get_data_as_dict())
        self.refresh_history_view()
        self.update_cumulative_gpa_display()
        
        self.clear_all(None)
        self.page.snack_bar.open = True
        self.page.update()

    def edit_semester(self, year, index):
        semesters = self.grade_manager.semesters_by_year.get(year, [])
        if not semesters or index >= len(semesters):
            return

        semester = semesters[index]
        
        # Load data back into form
        self.semester_name_field.value = semester.name
        self.year_dropdown.value = semester.year
        
        self.course_rows.controls.clear()
        for course in semester.courses:
            row = self.create_course_row()
            row.controls[0].value = course.name
            row.controls[1].value = str(course.credits)
            row.controls[2].value = course.grade
            self.course_rows.controls.append(row)
            
        # Set editing state
        self.editing_state["is_editing"] = True
        self.editing_state["year"] = year
        self.editing_state["index"] = index
        
        self.save_btn.text = "Update Semester"
        self.save_btn.icon = ft.Icons.UPDATE
        
        self.calculate_gpa_handler(None)
        self.page.update()

    def delete_semester(self, year, index):
        self.grade_manager.delete_semester(year, index)
        self.data_manager.save_data(self.grade_manager.get_data_as_dict())
        self.refresh_history_view()
        self.update_cumulative_gpa_display()
        self.page.update()

    def clear_all(self, e):
        self.semester_name_field.value = "Semester 1"
        self.course_rows.controls.clear()
        for _ in range(4):
            self.add_course_field(None)
        self.result_text.value = "GPA: 0.00"
        
        self.editing_state = {"is_editing": False, "year": None, "index": None}
        self.save_btn.text = "Save Semester"
        self.save_btn.icon = ft.Icons.SAVE
        
        self.page.update()

    def clear_history(self, e):
        self.grade_manager.semesters_by_year.clear()
        self.data_manager.save_data({})
        self.refresh_history_view()
        self.update_cumulative_gpa_display()
        self.page.update()

    def refresh_history_view(self):
        self.history_column.controls.clear()
        
        sorted_years = sorted(self.grade_manager.semesters_by_year.keys())
        
        for year in sorted_years:
            semesters = self.grade_manager.semesters_by_year[year]
            
            year_semesters_column = ft.Column(spacing=5)
            
            for i, semester in enumerate(semesters):
                gpa, _, credits = semester.calculate_stats()
                
                # Capture current values for closure
                current_year = year
                current_index = i
                
                year_semesters_column.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column([
                                    ft.Text(semester.name, weight="bold", color=ft.Colors.ON_SECONDARY_CONTAINER),
                                    ft.Text(f"Credits: {credits:.1f} | GPA: {gpa:.2f}", size=12, color=ft.Colors.ON_SECONDARY_CONTAINER),
                                ]),
                                ft.Row([
                                    ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.PRIMARY, tooltip="Edit", on_click=lambda e, y=current_year, idx=current_index: self.edit_semester(y, idx)),
                                    ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.ERROR, tooltip="Delete", on_click=lambda e, y=current_year, idx=current_index: self.delete_semester(y, idx)),
                                ])
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=10,
                        bgcolor=ft.Colors.SECONDARY_CONTAINER,
                        border_radius=5
                    )
                )
            
            self.history_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(year, size=16, weight="bold", color=ft.Colors.PRIMARY),
                        year_semesters_column
                    ]),
                    padding=ft.padding.only(bottom=10)
                )
            )
        self.page.update()

    def update_cumulative_gpa_display(self):
        cgpa = self.grade_manager.get_cumulative_gpa()
        self.cumulative_result_text.value = f"Cumulative GPA: {cgpa:.2f}"

    # --- Import Methods ---

    def open_import_dialog(self, e):
        self.page.open(self.import_dialog)

    def close_import_dialog(self, e):
        self.page.close(self.import_dialog)

    def run_import(self, e):
        text = self.import_text_field.value
        if not text:
            self.close_import_dialog(None)
            return

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        self.course_rows.controls.clear()
        
        i = 0
        while i < len(lines):
            if i + 4 >= len(lines):
                break
                
            code = lines[i]
            credits_str = lines[i+1]
            name_th = lines[i+2]
            name_en = lines[i+3]
            grade = lines[i+4]
            
            if "หน่วยกิต" not in credits_str:
                i += 1
                continue

            try:
                credits = float(credits_str.split()[0])
            except:
                credits = 0.0

            row = self.create_course_row()
            row.controls[0].value = f"{code} {name_en}"
            row.controls[1].value = str(credits)
            if grade in Course.GRADE_VALUES:
                row.controls[2].value = grade
            else:
                row.controls[2].value = None

            self.course_rows.controls.append(row)
            i += 5
        
        self.import_text_field.value = ""
        self.close_import_dialog(None)
        self.page.snack_bar = ft.SnackBar(ft.Text("Data imported successfully!"))
        self.page.snack_bar.open = True
        self.page.update()

    # --- Dashboard Methods ---

    def generate_charts(self, e):
        year_filter = self.dashboard_year_dropdown.value
        
        years = []
        gpas = []
        grade_counts = {}
        
        data = self.grade_manager.semesters_by_year
        
        if year_filter == "All Years":
            sorted_years = sorted(data.keys())
            for year in sorted_years:
                semesters = data[year]
                total_points = 0
                total_credits = 0
                for s in semesters:
                    _, p, c = s.calculate_stats()
                    total_points += p
                    total_credits += c
                    
                    for course in s.courses:
                        if course.grade:
                            grade_counts[course.grade] = grade_counts.get(course.grade, 0) + 1
                
                if total_credits > 0:
                    years.append(year)
                    gpas.append(total_points / total_credits)
        else:
            if year_filter in data:
                semesters = data[year_filter]
                for s in semesters:
                    gpa, _, _ = s.calculate_stats()
                    years.append(s.name)
                    gpas.append(gpa)
                    
                    for course in s.courses:
                        if course.grade:
                            grade_counts[course.grade] = grade_counts.get(course.grade, 0) + 1
        
        if not years and not grade_counts:
            self.dashboard_image.src_base64 = ""
            self.dashboard_image.update()
            return

        sns.set_theme(style="whitegrid")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
        fig.subplots_adjust(hspace=0.4)
        
        if years:
            sns.lineplot(x=years, y=gpas, ax=ax1, marker='o')
            ax1.set_title(f'GPA Summary ({year_filter})')
            ax1.set_ylabel('GPA')
            ax1.set_ylim(0, 4.0)
            for i, v in enumerate(gpas):
                ax1.text(i, v, f'{v:.2f}', ha='center', va='bottom')
        else:
            ax1.text(0.5, 0.5, 'No GPA Data', ha='center', va='center')

        if grade_counts:
            labels = list(grade_counts.keys())
            sizes = list(grade_counts.values())
            colors = sns.color_palette('pastel')[0:len(labels)]
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax2.axis('equal')
            ax2.set_title('Grade Distribution')
        else:
            ax2.text(0.5, 0.5, 'No Grade Data', ha='center', va='center')

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        self.dashboard_image.src_base64 = img_str
        self.dashboard_image.update()

    def download_chart(self, e):
        if not self.dashboard_image.src_base64:
            self.page.snack_bar = ft.SnackBar(ft.Text("No chart to download!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        try:
            img_data = base64.b64decode(self.dashboard_image.src_base64)
            filename = f"grade_chart_{self.dashboard_year_dropdown.value.replace(' ', '_')}.png"
            with open(filename, "wb") as f:
                f.write(img_data)
            
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Chart saved as {filename}"))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            print(f"Error saving chart: {ex}")

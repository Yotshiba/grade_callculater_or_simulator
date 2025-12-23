import flet as ft
from grade_calculator_app.ui import GradeCalculatorUI
from grade_calculator_app.data_manager import DataManager

def main(page: ft.Page):
    data_manager = DataManager("grade_data.json")
    app = GradeCalculatorUI(page, data_manager)

if __name__ == "__main__":
    ft.app(target=main)

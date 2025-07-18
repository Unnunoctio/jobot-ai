import shutil
import subprocess
from pathlib import Path


class LatexManager:
    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.latex_file = self.root / "latex" / "main.tex"
        self.output_pdf = self.root / "output" / "main.pdf"
        self.working_dir = self.latex_file.parent

    def compile(self) -> bool:
        command = ["latexmk", "-pdf", "-interaction=nonstopmode", "-silent", "-quiet", self.latex_file.name]

        try:
            subprocess.run(command, cwd=self.working_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            generated_pdf = self.working_dir / "main.pdf"
            shutil.move(str(generated_pdf), str(self.output_pdf))
            print("LaTeX file compiled successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print("Error while compiling LaTeX file.", e)
            return False
        except FileNotFoundError as e:
            print("Latexmk not found. Please install it and try again.", e)
            return False

    def write_objective(self, objective):
        objective_file = self.root / "latex" / "data" / "objective.csv"
        with open(objective_file, mode="w", newline="", encoding="utf-8") as of:
            of.write("objective\n")
            of.write(f'"{objective}"\n')

    def write_experiences(self, experiences):
        experiences_file = self.root / "latex" / "data" / "experience.csv"
        with open(experiences_file, mode="w", newline="", encoding="utf-8") as of:
            of.write("company,position,period,tasks\n")
            for exp in experiences:
                of.write(f'"{exp[0]}","{exp[1]}","{exp[2]}","{exp[3]}"\n')


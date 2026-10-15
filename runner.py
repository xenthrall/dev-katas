# runner.py
import subprocess
import sys
import time
from pathlib import Path

from rich.syntax import Syntax
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DirectoryTree, Footer, Header, RichLog, Static


class PythonKataTree(DirectoryTree):
    """Árbol de directorios filtrado para mostrar solo carpetas y scripts .py"""

    def filter_paths(self, paths: list[Path]) -> list[Path]:
        filtered = []
        for path in paths:
            if path.name.startswith((".", "__")):
                continue
            if path.is_dir() or path.suffix == ".py":
                filtered.append(path)
        return sorted(filtered, key=lambda p: (not p.is_dir(), p.name.lower()))


class KataRunnerApp(App):
    """TUI interactiva con soporte de ratón y teclado para ejecutar katas."""

    TITLE = "⚡ DEV-KATAS STUDIO"
    SUB_TITLE = "Python Deliberate Practice & Live-Coding Runner"

    CSS = """
    Screen {
        background: #0f172a;
    }

    #main-container {
        height: 1fr;
        padding: 1 2;
    }

    /* Panel Izquierdo: Explorador */
    #sidebar {
        width: 38%;
        min-width: 34;
        height: 1fr;
        background: #1e293b;
        border: round #38bdf8;
        padding: 0 1;
        margin-right: 1;
    }

    #sidebar-title {
        text-style: bold;
        color: #38bdf8;
        padding: 1 1 0 1;
        margin-bottom: 1;
    }

    PythonKataTree {
        background: transparent;
        scrollbar-gutter: stable;
    }

    PythonKataTree > .directory-tree--folder {
        color: #f8fafc;
        text-style: bold;
    }

    PythonKataTree > .directory-tree--file {
        color: #10b981;
    }

    /* Panel Derecho: Vista de Código y Consola */
    #workspace {
        width: 62%;
        height: 1fr;
    }

    #status-bar {
        height: 3;
        background: #1e293b;
        border: round #475569;
        content-align: left middle;
        padding: 0 2;
        color: #e2e8f0;
        margin-bottom: 1;
    }

    #code-preview-box {
        height: 1fr;
        background: #090d16;
        border: round #334155;
        padding: 0 1;
        margin-bottom: 1;
    }

    #output-box {
        height: 1fr;
        background: #090d16;
        border: round #10b981;
        padding: 0 1;
    }

    .panel-header {
        color: #94a3b8;
        text-style: bold;
        padding: 0 1;
        background: #1e293b;
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("r", "run_selected", "🚀 Ejecutar (R)", show=True),
        Binding("c", "clear_output", "🧹 Limpiar Consola (C)", show=True),
        Binding("q", "quit", "❌ Salir (Q)", show=True),
    ]

    def __init__(self, base_dir: Path):
        super().__init__()
        self.base_dir = base_dir
        self.current_script: Path | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                yield Static("📂 EXPLORADOR DE KATAS (Clic o ↑/↓)", id="sidebar-title")
                yield PythonKataTree(str(self.base_dir), id="kata-tree")

            with Vertical(id="workspace"):
                yield Static(
                    "👉 Haz clic o presiona [bold cyan]Enter[/] sobre un archivo [bold green].py[/] para cargarlo y ejecutarlo.",
                    id="status-bar",
                )
                yield RichLog(id="code-preview-box", highlight=True, markup=True, wrap=False)
                yield RichLog(id="output-box", highlight=True, markup=True, wrap=True)
        yield Footer()

    def on_mount(self) -> None:
        preview_box = self.query_one("#code-preview-box", RichLog)
        preview_box.border_title = "📄 Previsualización de Código"

        output_box = self.query_one("#output-box", RichLog)
        output_box.border_title = "💻 Consola de Ejecución & Métricas"
        output_box.write("[dim]Selecciona un script a la izquierda para ver su resultado aquí...[/dim]")

        tree = self.query_one("#kata-tree", PythonKataTree)
        tree.root.expand()

    @on(DirectoryTree.FileSelected)
    def handle_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Se dispara al hacer clic con el ratón o presionar Enter sobre un archivo .py"""
        script_path = Path(event.path)
        if script_path.suffix != ".py":
            return

        self.current_script = script_path
        self.load_code_preview(script_path)
        self.execute_script(script_path)

    def load_code_preview(self, script_path: Path) -> None:
        preview_box = self.query_one("#code-preview-box", RichLog)
        preview_box.clear()
        try:
            code = script_path.read_text(encoding="utf-8")
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True, word_wrap=False)
            preview_box.write(syntax)
        except Exception as e:
            preview_box.write(f"[bold red]Error leyendo archivo:[/] {e}")

    @work(exclusive=True, thread=True)
    def execute_script(self, script_path: Path) -> None:
        rel_path = script_path.relative_to(self.base_dir.parent)
        status_bar = self.query_one("#status-bar", Static)
        output_box = self.query_one("#output-box", RichLog)

        self.call_from_thread(
            status_bar.update,
            f"⏳ Ejecutando: [bold cyan]{rel_path}[/] ...",
        )
        self.call_from_thread(output_box.clear)
        self.call_from_thread(
            output_box.write,
            f"[bold cyan]▶ Running {rel_path}[/bold cyan]\n" + "─" * 60,
        )

        start = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        if proc.stdout:
            self.call_from_thread(output_box.write, Text(proc.stdout.rstrip()))
        if proc.stderr:
            self.call_from_thread(output_box.write, Text(proc.stderr.rstrip(), style="bold red"))

        if not proc.stdout and not proc.stderr:
            self.call_from_thread(output_box.write, "[dim italic](El script terminó sin imprimir salida en consola)[/]")

        self.call_from_thread(output_box.write, "─" * 60)

        if proc.returncode == 0:
            badge = f"✅ [bold green]PASSED[/]  |  ⏱️  [bold yellow]{elapsed_ms:.2f} ms[/]  |  📄 [bold white]{rel_path}[/]"
            self.call_from_thread(
                output_box.write,
                f"[bold green]✔ Execution finished successfully in {elapsed_ms:.2f} ms[/]",
            )
            output_box.styles.border = ("round", "#10b981")
        else:
            badge = f"❌ [bold red]FAILED (Code {proc.returncode})[/]  |  ⏱️  [bold yellow]{elapsed_ms:.2f} ms[/]  |  📄 [bold white]{rel_path}[/]"
            self.call_from_thread(
                output_box.write,
                f"[bold red]✖ Execution failed (Exit code {proc.returncode}) in {elapsed_ms:.2f} ms[/]",
            )
            output_box.styles.border = ("round", "#ef4444")

        self.call_from_thread(status_bar.update, badge)

    def action_run_selected(self) -> None:
        """Atajo 'R' para re-ejecutar el script actual al instante."""
        if self.current_script and self.current_script.exists():
            self.load_code_preview(self.current_script)
            self.execute_script(self.current_script)
        else:
            status_bar = self.query_one("#status-bar", Static)
            status_bar.update("⚠️  [bold yellow]Primero selecciona un script .py en el panel izquierdo.[/]")

    def action_clear_output(self) -> None:
        """Atajo 'C' para limpiar la consola."""
        output_box = self.query_one("#output-box", RichLog)
        output_box.clear()


def main():
    base_dir = Path(__file__).resolve().parent / "python"
    if not base_dir.exists():
        print(f"Error: No se encontró el directorio {base_dir}")
        sys.exit(1)

    app = KataRunnerApp(base_dir=base_dir)
    app.run()


if __name__ == "__main__":
    main()
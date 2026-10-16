# runner.py
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DirectoryTree, Footer, Header, Input, MarkdownViewer, RichLog, Static, TextArea

PROJECT_ROOT = Path(__file__).resolve().parent
PYTHON_DIR = PROJECT_ROOT / "python"
NOTES_DIR = PROJECT_ROOT / "notes"
CACHE_DIR = PROJECT_ROOT / ".katas_cache"
SOLUTIONS_BACKUP_FILE = CACHE_DIR / "solutions_backup.json"

PRACTICE_MARKER = 'raise NotImplementedError("Pendiente de implementar")'
SOLUTION_BLOCK_RE = re.compile(
    r"(?P<indent>[ \t]*)# BEGIN_SOLUTION\r?\n(?P<body>.*?)(?P=indent)# END_SOLUTION",
    re.DOTALL,
)


class KataSolutionManager:
    """Gestiona el respaldo de soluciones, el Modo Práctica (sin IA) y la extracción de pistas."""

    def __init__(self, root_dir: Path = PROJECT_ROOT, backup_file: Path = SOLUTIONS_BACKUP_FILE) -> None:
        self.root_dir = root_dir
        self.backup_file = backup_file

    def _rel_key(self, file_path: Path) -> str:
        return file_path.resolve().relative_to(self.root_dir.resolve()).as_posix()

    def _load_backups(self) -> dict[str, list[str]]:
        if not self.backup_file.exists():
            return {}
        try:
            return json.loads(self.backup_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_backups(self, data: dict[str, list[str]]) -> None:
        self.backup_file.parent.mkdir(parents=True, exist_ok=True)
        self.backup_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def ensure_backup(self, script_path: Path) -> list[str]:
        """Guarda los bloques # BEGIN_SOLUTION ... # END_SOLUTION originales si contienen soluciones reales."""
        content = script_path.read_text(encoding="utf-8")
        matches = list(SOLUTION_BLOCK_RE.finditer(content))
        if not matches:
            return []

        key = self._rel_key(script_path)
        backups = self._load_backups()
        existing = backups.get(key, [])

        current_bodies = [m.group("body") for m in matches]
        updated_bodies: list[str] = []

        for idx, body in enumerate(current_bodies):
            if PRACTICE_MARKER not in body:
                updated_bodies.append(body)
            elif idx < len(existing):
                updated_bodies.append(existing[idx])
            else:
                updated_bodies.append(body)

        if any(PRACTICE_MARKER not in b for b in updated_bodies):
            backups[key] = updated_bodies
            self._save_backups(backups)

        return backups.get(key, current_bodies)

    def is_in_practice_mode(self, script_path: Path) -> tuple[bool, int, int]:
        """Devuelve (tiene_pendientes, bloques_pendientes, total_bloques)."""
        if not script_path.exists() or script_path.suffix != ".py":
            return False, 0, 0
        content = script_path.read_text(encoding="utf-8")
        matches = list(SOLUTION_BLOCK_RE.finditer(content))
        total = len(matches)
        pending = sum(1 for m in matches if PRACTICE_MARKER in m.group("body"))
        return pending > 0, pending, total

    def enable_practice_mode(self, script_path: Path) -> int:
        """Reemplaza las soluciones entre # BEGIN_SOLUTION y # END_SOLUTION por NotImplementedError."""
        self.ensure_backup(script_path)
        content = script_path.read_text(encoding="utf-8")
        count = 0

        def _replacer(match: re.Match[str]) -> str:
            nonlocal count
            count += 1
            indent = match.group("indent")
            return (
                f"{indent}# BEGIN_SOLUTION\n"
                f"{indent}# TODO: Implementa tu solución aquí de memoria (Presiona 'H' para pistas o 'S' para restaurar)\n"
                f"{indent}{PRACTICE_MARKER}\n"
                f"{indent}# END_SOLUTION"
            )

        new_content = SOLUTION_BLOCK_RE.sub(_replacer, content)
        if count > 0:
            script_path.write_text(new_content, encoding="utf-8")
        return count

    def restore_solutions(self, script_path: Path) -> tuple[bool, int]:
        """Restaura las soluciones oficiales desde la caché de respaldo."""
        key = self._rel_key(script_path)
        backups = self._load_backups()
        saved_bodies = backups.get(key)
        if not saved_bodies:
            return False, 0

        content = script_path.read_text(encoding="utf-8")
        idx = 0

        def _replacer(match: re.Match[str]) -> str:
            nonlocal idx
            indent = match.group("indent")
            body = saved_bodies[idx] if idx < len(saved_bodies) else match.group("body")
            idx += 1
            return f"{indent}# BEGIN_SOLUTION\n{body}{indent}# END_SOLUTION"

        new_content = SOLUTION_BLOCK_RE.sub(_replacer, content)
        script_path.write_text(new_content, encoding="utf-8")
        return True, idx

    def get_reference_code(self, script_path: Path) -> str:
        """Devuelve el código completo con las soluciones restauradas en memoria (sin tocar el disco)."""
        self.ensure_backup(script_path)
        key = self._rel_key(script_path)
        backups = self._load_backups()
        saved_bodies = backups.get(key)
        content = script_path.read_text(encoding="utf-8")
        if not saved_bodies:
            return content

        idx = 0

        def _replacer(match: re.Match[str]) -> str:
            nonlocal idx
            indent = match.group("indent")
            body = saved_bodies[idx] if idx < len(saved_bodies) else match.group("body")
            idx += 1
            return f"{indent}# BEGIN_SOLUTION\n{body}{indent}# END_SOLUTION"

        return SOLUTION_BLOCK_RE.sub(_replacer, content)

    def extract_study_guide_and_hints(self, script_path: Path) -> str:
        """Extrae la guía de sintaxis del módulo y los docstrings/pistas de cada ejercicio sin revelar código."""
        content = script_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(content)
        except SyntaxError as exc:
            return f"# Error de sintaxis en el archivo actual:\n{exc}"

        sections: list[str] = []
        mod_doc = ast.get_docstring(tree)
        if mod_doc:
            sections.append(mod_doc.strip())

        sections.append("\n" + "═" * 72)
        sections.append("🎯 ENUNCIADOS Y PISTAS DE EJERCICIOS (MODO SIN SPOILERS)")
        sections.append("═" * 72 + "\n")

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith(("check_", "test_", "run_", "_")):
                    continue
                doc = ast.get_docstring(node)
                if not doc:
                    continue
                prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                args_str = ast.unparse(node.args) if hasattr(ast, "unparse") else "..."
                ret_str = f" -> {ast.unparse(node.returns)}" if node.returns and hasattr(ast, "unparse") else ""
                sections.append(f"🔹 {prefix} {node.name}({args_str}){ret_str}:")
                for line in doc.strip().splitlines():
                    sections.append(f"    {line}")
                sections.append("")
            elif isinstance(node, ast.ClassDef):
                if node.name.startswith(("_", "Test")):
                    continue
                doc = ast.get_docstring(node)
                sections.append(f"🏛️ class {node.name}:")
                if doc:
                    for line in doc.strip().splitlines():
                        sections.append(f"    {line}")
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        sub_doc = ast.get_docstring(sub)
                        if sub_doc:
                            sections.append(f"\n    ▸ def {sub.name}(...):")
                            for line in sub_doc.strip().splitlines():
                                sections.append(f"        {line}")
                sections.append("")

        return "\n".join(sections)


class PythonKataTree(DirectoryTree):
    """Árbol de directorios para explorar manuales (.md) y katas (.py) con filtrado en vivo."""

    def __init__(self, path: str, **kwargs: Any) -> None:
        super().__init__(path, **kwargs)
        self.search_query: str = ""

    def _matches_query(self, path: Path) -> bool:
        if not self.search_query:
            return True
        q = self.search_query.lower()
        if q in path.name.lower() or q in path.as_posix().lower():
            return True
        if path.is_file() and path.suffix in (".py", ".md"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
                return q in text
            except Exception:
                return False
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix in (".py", ".md"):
                    if not any(part.startswith((".", "__")) for part in child.parts):
                        if self._matches_query(child):
                            return True
        return False

    def filter_paths(self, paths: list[Path]) -> list[Path]:
        filtered: list[Path] = []
        for path in paths:
            if path.name.startswith((".", "__")):
                continue
            if path.is_dir() or path.suffix in (".py", ".md"):
                if self._matches_query(path):
                    filtered.append(path)
        return sorted(filtered, key=lambda p: (not p.is_dir(), p.name.lower()))


class KataRunnerApp(App):
    """Estudio interactivo TUI para estudiar sintaxis de Python y practicar katas sin IA."""

    TITLE = "⚡ DEV-KATAS PYTHON STUDIO"
    SUB_TITLE = "Referencia de Sintaxis, Internals & Práctica Deliberada Sin IA"

    CSS = """
    Screen {
        background: #0f172a;
    }

    #main-container {
        height: 1fr;
        padding: 1 2;
    }

    /* Panel Izquierdo: Buscador y Explorador */
    #sidebar {
        width: 32%;
        min-width: 30;
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
    }

    #search-input {
        margin: 1 0;
        background: #090d16;
        border: tall #475569;
        color: #f8fafc;
    }

    #search-input:focus {
        border: tall #38bdf8;
    }

    PythonKataTree {
        background: transparent;
        scrollbar-gutter: stable;
        height: 1fr;
    }

    PythonKataTree > .directory-tree--folder {
        color: #f8fafc;
        text-style: bold;
    }

    PythonKataTree > .directory-tree--file {
        color: #10b981;
    }

    /* Panel Derecho: Vista de Estudio/Código y Consola */
    #workspace {
        width: 1fr;
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

    #markdown-viewer {
        height: 2fr;
        background: #090d16;
        border: round #38bdf8;
        margin-bottom: 1;
    }

    #code-preview-box {
        height: 2fr;
        background: #090d16;
        border: round #334155;
        padding: 0 1;
        margin-bottom: 1;
        display: none;
    }

    #playground-editor {
        height: 2fr;
        background: #090d16;
        border: round #f59e0b;
        padding: 0 1;
        margin-bottom: 1;
        display: none;
    }

    #playground-editor:focus {
        border: round #38bdf8;
    }

    #output-box {
        height: 1fr;
        background: #090d16;
        border: round #10b981;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("r", "run_selected", "🚀 Ejecutar (R)", show=True),
        Binding("ctrl+r", "save_and_run_playground", "▶️ Ejecutar Editor (Ctrl+R)", show=True, priority=True),
        Binding("f5", "save_and_run_playground", "Ejecutar (F5)", show=False, priority=True),
        Binding("x", "open_playground", "🧪 Playground (X)", show=True),
        Binding("b", "toggle_sidebar", "📂 Árbol (B)", show=True),
        Binding("ctrl+b", "toggle_sidebar", "Árbol (Ctrl+B)", show=False, priority=True),
        Binding("t", "toggle_console", "💻 Consola (T)", show=True),
        Binding("ctrl+t", "toggle_console", "Consola (Ctrl+T)", show=False, priority=True),
        Binding("m", "maximize_console", "🔍 Max Consola (M)", show=True),
        Binding("f9", "maximize_console", "Max Consola (F9)", show=False, priority=True),
        Binding("z", "zen_mode", "🧘 Zen (Z)", show=True),
        Binding("f11", "zen_mode", "Modo Zen (F11)", show=False, priority=True),
        Binding("i", "toggle_toc", "📑 Índice MD (I)", show=True),
        Binding("p", "practice_mode", "🎯 Práctica (P)", show=True),
        Binding("h", "show_hints", "💡 Pistas (H)", show=True),
        Binding("v", "peek_solutions", "👁️ Espiar (V)", show=True),
        Binding("s", "restore_solutions", "♻️ Restaurar (S)", show=True),
        Binding("a", "run_all_audit", "📊 Auditoría (A)", show=True),
        Binding("slash", "focus_search", "🔍 Buscar (/)", show=True),
        Binding("escape", "clear_search", "Salir al Árbol (Esc)", show=False, priority=True),
        Binding("c", "clear_output", "🧹 Limpiar (C)", show=False),
        Binding("q", "quit", "❌ Salir (Q)", show=True),
    ]

    def __init__(self, base_dir: Path) -> None:
        super().__init__()
        self.base_dir = base_dir
        self.current_file: Path | None = None
        self.solution_mgr = KataSolutionManager(root_dir=PROJECT_ROOT)
        self._loading_playground: bool = False
        self._active_upper_view: str = "markdown"
        self._console_maximized: bool = False

    def _is_playground(self, path: Path | None) -> bool:
        if path is None:
            return False
        try:
            return path.resolve() == (self.base_dir / "playground.py").resolve()
        except Exception:
            return False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                yield Static("📂 CURRÍCULO PYTHON (00–99)", id="sidebar-title")
                yield Input(
                    placeholder="🔍 Buscar sintaxis o método (/)...",
                    id="search-input",
                )
                yield PythonKataTree(str(self.base_dir), id="kata-tree")

            with Vertical(id="workspace"):
                yield Static(
                    "👉 [bold cyan]B[/]=Colapsar Árbol  [bold cyan]T[/]=Ocultar Consola  "
                    "[bold cyan]M[/]=Maximizar Consola  [bold cyan]Z[/]=Modo Zen  [bold cyan]X[/]=Playground",
                    id="status-bar",
                )
                yield MarkdownViewer(
                    "",
                    show_table_of_contents=True,
                    id="markdown-viewer",
                )
                yield RichLog(id="code-preview-box", highlight=True, markup=True, wrap=True)
                yield TextArea.code_editor(
                    "",
                    language="python",
                    theme="monokai",
                    id="playground-editor",
                    show_line_numbers=True,
                    tab_behavior="indent",
                )
                yield RichLog(id="output-box", highlight=True, markup=True, wrap=True)
        yield Footer()

    def on_mount(self) -> None:
        md_viewer = self.query_one("#markdown-viewer", MarkdownViewer)
        md_viewer.can_focus = True
        md_viewer.border_title = "📖 Lector Markdown Interactivo (I = Mostrar/Ocultar Índice)"

        preview_box = self.query_one("#code-preview-box", RichLog)
        preview_box.can_focus = True
        preview_box.border_title = "📄 Visor de Estudio, Sintaxis y Código"

        editor = self.query_one("#playground-editor", TextArea)
        editor.border_title = (
            "🧪 Editor en Vivo: python/playground.py  |  "
            "Ctrl+R = Ejecutar  |  Ctrl+B = Árbol  |  Ctrl+T = Consola  |  Esc = Salir"
        )

        output_box = self.query_one("#output-box", RichLog)
        output_box.can_focus = True
        output_box.border_title = "💻 Consola de Verificación, Tests & Métricas (T = Ocultar | M = Maximizar)"
        output_box.write(
            "[bold cyan]Bienvenido a DEV-KATAS PYTHON STUDIO[/bold cyan]\n"
            "• [bold yellow]Organización de Paneles:[/] Presiona [bold cyan]B[/] (o [bold]Ctrl+B[/]) para colapsar el árbol lateral, "
            "[bold cyan]T[/] (o [bold]Ctrl+T[/]) para ocultar/mostrar esta consola, [bold cyan]M[/] (o [bold]F9[/]) para maximizar la consola, "
            "o [bold cyan]Z[/] (o [bold]F11[/]) para Modo Zen a pantalla completa.\n"
            "• [bold yellow]Lectura Markdown (.md):[/] Usa el lector nativo con tabla de contenidos interactiva ([bold cyan]I[/] para alternar el índice).\n"
            "• [bold yellow]Playground en Vivo:[/] Presiona [bold cyan]X[/] para escribir código en [bold]playground.py[/] y [bold cyan]Ctrl+R[/] para ejecutarlo."
        )

        tree = self.query_one("#kata-tree", PythonKataTree)
        tree.root.expand()
        tree.focus()

        readme_path = self.base_dir / "README.md"
        if not readme_path.exists():
            readme_path = self.base_dir / "00-cheatsheets-and-reference" / "05_syntax_search_index.md"
        if readme_path.exists():
            self.current_file = readme_path
            self.load_markdown_preview(readme_path)

    def _set_upper_view(self, view_mode: str) -> None:
        """Activa exactamente uno de los visores superiores: 'markdown', 'code' o 'playground'."""
        self._active_upper_view = view_mode
        self._console_maximized = False

        md_viewer = self.query_one("#markdown-viewer", MarkdownViewer)
        preview_box = self.query_one("#code-preview-box", RichLog)
        editor = self.query_one("#playground-editor", TextArea)

        md_viewer.display = view_mode == "markdown"
        preview_box.display = view_mode == "code"
        editor.display = view_mode == "playground"

    def _ensure_console_visible(self) -> None:
        """Muestra la consola inferior cuando se ejecuta código o una búsqueda."""
        output_box = self.query_one("#output-box", RichLog)
        if not output_box.display:
            output_box.display = True

    @on(Input.Changed, "#search-input")
    def handle_search_changed(self, event: Input.Changed) -> None:
        tree = self.query_one("#kata-tree", PythonKataTree)
        tree.search_query = event.value.strip()
        tree.reload()
        tree.root.expand()

    @on(Input.Submitted, "#search-input")
    def handle_search_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if query:
            self.run_syntax_search_in_console(query)
        self.query_one("#kata-tree", PythonKataTree).focus()

    @on(TextArea.Changed, "#playground-editor")
    def handle_playground_changed(self, event: TextArea.Changed) -> None:
        if self._loading_playground:
            return
        playground_path = self.base_dir / "playground.py"
        try:
            playground_path.write_text(event.text_area.text, encoding="utf-8")
        except Exception:
            pass

    @on(DirectoryTree.FileSelected)
    def handle_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        selected_path = Path(event.path)
        self.current_file = selected_path

        if self._is_playground(selected_path):
            self.open_playground_editor(selected_path, focus_editor=True)
            self.execute_script(selected_path)
        elif selected_path.suffix == ".md":
            self.load_markdown_preview(selected_path)
        elif selected_path.suffix == ".py":
            self.solution_mgr.ensure_backup(selected_path)
            self.load_code_preview(selected_path)
            self.execute_script(selected_path)

    def _show_readonly_preview(self) -> RichLog:
        self._set_upper_view("code")
        return self.query_one("#code-preview-box", RichLog)

    def open_playground_editor(self, playground_path: Path, focus_editor: bool = True) -> None:
        self._set_upper_view("playground")
        editor = self.query_one("#playground-editor", TextArea)
        status_bar = self.query_one("#status-bar", Static)

        editor.border_title = (
            "🧪 Editor en Vivo: python/playground.py  |  "
            "Ctrl+R = Ejecutar  |  Ctrl+B = Árbol  |  Ctrl+T = Consola  |  Esc = Salir"
        )
        try:
            content = playground_path.read_text(encoding="utf-8")
        except Exception:
            content = 'print("Hola mundo")\n'

        if editor.text != content:
            self._loading_playground = True
            try:
                editor.load_text(content)
            finally:
                self._loading_playground = False

        if focus_editor:
            editor.focus()

        status_bar.update(
            "🧪 [bold yellow]Editando python/playground.py[/]  |  "
            "[bold cyan]Ctrl+R[/]=Ejecutar  [bold cyan]Ctrl+B[/]=Árbol  [bold cyan]Ctrl+T[/]=Consola  [bold cyan]F11[/]=Zen"
        )

    def load_markdown_preview(self, md_path: Path) -> None:
        self._set_upper_view("markdown")
        md_viewer = self.query_one("#markdown-viewer", MarkdownViewer)
        output_box = self.query_one("#output-box", RichLog)
        status_bar = self.query_one("#status-bar", Static)

        # Al abrir un archivo .md, ocultamos la consola automáticamente para dar máxima altura de lectura
        output_box.display = False

        rel_path = md_path.relative_to(PROJECT_ROOT)
        toc_state = "Visible" if md_viewer.show_table_of_contents else "Oculto"
        md_viewer.border_title = f"📖 Manual Markdown: {rel_path}  |  📑 Índice: {toc_state} (I)  |  🧘 Zen (Z)"
        try:
            content = md_path.read_text(encoding="utf-8")
            md_viewer.document.update(content)
            status_bar.update(
                f"📖 Leyendo [bold yellow]{rel_path}[/]  |  "
                "[bold cyan]B[/]=Colapsar Árbol  [bold cyan]I[/]=Índice MD  [bold cyan]Z[/]=Pantalla Completa  [bold cyan]T[/]=Consola"
            )
        except Exception as exc:
            md_viewer.document.update(f"# Error leyendo manual Markdown\n\n`{exc}`")

    def load_code_preview(self, script_path: Path, custom_code: str | None = None, title_prefix: str = "📄 Código") -> None:
        if self._is_playground(script_path) and custom_code is None:
            self.open_playground_editor(script_path, focus_editor=False)
            return

        preview_box = self._show_readonly_preview()
        preview_box.clear()
        rel_path = script_path.relative_to(PROJECT_ROOT)
        in_practice, pending, total = self.solution_mgr.is_in_practice_mode(script_path)
        mode_tag = f"🎯 MODO PRÁCTICA ({total - pending}/{total} resueltos)" if in_practice else "📚 MODO ESTUDIO (Resuelto)"
        preview_box.border_title = f"{title_prefix}: {rel_path}  |  {mode_tag}"
        try:
            code = custom_code if custom_code is not None else script_path.read_text(encoding="utf-8")
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True, word_wrap=False)
            preview_box.write(syntax)
        except Exception as exc:
            preview_box.write(f"[bold red]Error leyendo archivo:[/] {exc}")

    @work(exclusive=True, thread=True)
    def execute_script(self, script_path: Path) -> None:
        rel_path = script_path.relative_to(PROJECT_ROOT)
        status_bar = self.query_one("#status-bar", Static)
        output_box = self.query_one("#output-box", RichLog)

        self.call_from_thread(self._ensure_console_visible)

        is_pg = self._is_playground(script_path)
        in_practice, pending, total = self.solution_mgr.is_in_practice_mode(script_path)
        if is_pg:
            mode_badge = "[bold yellow]🧪 PLAYGROUND EN VIVO (Ctrl+R)[/]"
        elif in_practice:
            mode_badge = f"[bold magenta]🎯 PRÁCTICA ({total - pending}/{total})[/]"
        else:
            mode_badge = "[bold cyan]📚 ESTUDIO[/]"

        self.call_from_thread(
            status_bar.update,
            f"⏳ Ejecutando: [bold cyan]{rel_path}[/] ({mode_badge}) ...",
        )
        self.call_from_thread(output_box.clear)
        self.call_from_thread(
            output_box.write,
            f"[bold cyan]▶ Running {rel_path}[/bold cyan]  ({mode_badge})\n" + "─" * 68,
        )

        start = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(PROJECT_ROOT),
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        if proc.stdout:
            self.call_from_thread(output_box.write, Text(proc.stdout.rstrip()))
        if proc.stderr:
            self.call_from_thread(output_box.write, Text(proc.stderr.rstrip(), style="bold red"))

        if not proc.stdout and not proc.stderr:
            self.call_from_thread(output_box.write, "[dim italic](El script terminó sin imprimir salida en consola)[/]")

        self.call_from_thread(output_box.write, "─" * 68)

        if proc.returncode == 0:
            badge = (
                f"✅ [bold green]PASSED[/]  |  {mode_badge}  |  "
                f"⏱️ [bold yellow]{elapsed_ms:.1f} ms[/]  |  📄 [bold white]{rel_path}[/]  |  [bold cyan]M[/]=Max Consola"
            )
            self.call_from_thread(
                output_box.write,
                f"[bold green]✔ Ejecución completada con éxito en {elapsed_ms:.1f} ms[/]",
            )
            output_box.styles.border = ("round", "#10b981")
        elif in_practice and "PENDIENTE" in (proc.stdout or ""):
            badge = (
                f"🎯 [bold magenta]EN PRÁCTICA ({total - pending}/{total} implementados)[/]  |  "
                f"⏱️ [bold yellow]{elapsed_ms:.1f} ms[/]  |  📄 [bold white]{rel_path}[/]"
            )
            self.call_from_thread(
                output_box.write,
                "[bold magenta]💡 Implementa los ejercicios marcados con TODO en tu editor y presiona 'R' para volver a probar.[/]",
            )
            output_box.styles.border = ("round", "#a855f7")
        else:
            badge = (
                f"❌ [bold red]FAILED (Exit {proc.returncode})[/]  |  {mode_badge}  |  "
                f"⏱️ [bold yellow]{elapsed_ms:.1f} ms[/]  |  📄 [bold white]{rel_path}[/]  |  [bold cyan]M[/]=Max Consola"
            )
            self.call_from_thread(
                output_box.write,
                f"[bold red]✖ Error en la ejecución ({elapsed_ms:.1f} ms). Presiona 'M' (o F9) para maximizar la consola.[/]",
            )
            output_box.styles.border = ("round", "#ef4444")

        self.call_from_thread(status_bar.update, badge)

    def _focus_active_workspace(self) -> None:
        if self._console_maximized:
            self.query_one("#output-box", RichLog).focus()
        elif self._active_upper_view == "playground":
            self.query_one("#playground-editor", TextArea).focus()
        elif self._active_upper_view == "code":
            self.query_one("#code-preview-box", RichLog).focus()
        else:
            self.query_one("#markdown-viewer", MarkdownViewer).focus()

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar", Vertical)
        status_bar = self.query_one("#status-bar", Static)
        if sidebar.display:
            self._focus_active_workspace()
            sidebar.display = False
            status_bar.update("📖 [bold green]Árbol lateral colapsado[/] — Espacio horizontal máximo activado ([bold]B[/] / [bold]Ctrl+B[/] para mostrar)")
        else:
            sidebar.display = True
            if self._active_upper_view != "playground":
                self.query_one("#kata-tree", PythonKataTree).focus()
            status_bar.update("📂 [bold cyan]Árbol de navegación expandido[/] (Presiona [bold]B[/] o [bold]Ctrl+B[/] para colapsar)")

    def action_toggle_console(self) -> None:
        output_box = self.query_one("#output-box", RichLog)
        status_bar = self.query_one("#status-bar", Static)

        if self._console_maximized:
            self._set_upper_view(self._active_upper_view)
            output_box.display = False
            self._focus_active_workspace()
            status_bar.update("💻 [bold yellow]Consola oculta[/] — Visor/Editor a altura completa ([bold]T[/] / [bold]Ctrl+T[/] para mostrar)")
            return

        output_box.display = not output_box.display
        if output_box.display:
            status_bar.update("💻 [bold green]Consola visible[/] ([bold]T[/] / [bold]Ctrl+T[/] para ocultar | [bold]M[/] / [bold]F9[/] para maximizar)")
        else:
            self._focus_active_workspace()
            status_bar.update("💻 [bold yellow]Consola oculta[/] — Visor/Editor a altura completa ([bold]T[/] / [bold]Ctrl+T[/] para mostrar)")

    def action_maximize_console(self) -> None:
        output_box = self.query_one("#output-box", RichLog)
        md_viewer = self.query_one("#markdown-viewer", MarkdownViewer)
        preview_box = self.query_one("#code-preview-box", RichLog)
        editor = self.query_one("#playground-editor", TextArea)
        status_bar = self.query_one("#status-bar", Static)

        if not self._console_maximized:
            self._console_maximized = True
            md_viewer.display = False
            preview_box.display = False
            editor.display = False
            output_box.display = True
            output_box.focus()
            status_bar.update(
                "🔍 [bold green]Consola Maximizada a Pantalla Completa[/] — "
                "Presiona [bold cyan]M[/] (o [bold cyan]F9[/]) para volver al visor/editor"
            )
        else:
            self._set_upper_view(self._active_upper_view)
            output_box.display = True
            self._focus_active_workspace()
            status_bar.update("🔄 [bold cyan]Vista dividida restaurada[/] (Visor superior + Consola inferior)")

    def action_zen_mode(self) -> None:
        sidebar = self.query_one("#sidebar", Vertical)
        output_box = self.query_one("#output-box", RichLog)
        status_bar = self.query_one("#status-bar", Static)

        entering_zen = sidebar.display or output_box.display or self._console_maximized
        if entering_zen:
            self._set_upper_view(self._active_upper_view)
            self._focus_active_workspace()
            sidebar.display = False
            output_box.display = False
            status_bar.update(
                "🧘 [bold magenta]MODO ZEN ACTIVADO (100% Pantalla Completa)[/] — "
                "Presiona [bold cyan]Z[/] (o [bold cyan]F11[/]) para restaurar paneles"
            )
        else:
            sidebar.display = True
            if self._active_upper_view != "markdown":
                output_box.display = True
            if self._active_upper_view != "playground":
                self.query_one("#kata-tree", PythonKataTree).focus()
            status_bar.update("🔄 [bold cyan]Modo Zen desactivado — Paneles restaurados[/]")

    def action_toggle_toc(self) -> None:
        md_viewer = self.query_one("#markdown-viewer", MarkdownViewer)
        status_bar = self.query_one("#status-bar", Static)
        if not md_viewer.display:
            status_bar.update("ℹ️ [bold yellow]Abre un archivo .md para alternar su Tabla de Contenidos (I).[/]")
            return
        md_viewer.show_table_of_contents = not md_viewer.show_table_of_contents
        state_str = "mostrada" if md_viewer.show_table_of_contents else "oculta"
        status_bar.update(f"📑 [bold cyan]Tabla de Contenidos (TOC) {state_str}[/] (Presiona [bold]I[/] para alternar)")

    def action_focus_search(self) -> None:
        sidebar = self.query_one("#sidebar", Vertical)
        if not sidebar.display:
            sidebar.display = True
        self.query_one("#search-input", Input).focus()

    def action_clear_search(self) -> None:
        sidebar = self.query_one("#sidebar", Vertical)
        if not sidebar.display:
            sidebar.display = True
        search_input = self.query_one("#search-input", Input)
        if search_input.has_focus and search_input.value:
            search_input.value = ""
        self.query_one("#kata-tree", PythonKataTree).focus()

    def action_save_and_run_playground(self) -> None:
        playground_path = self.base_dir / "playground.py"
        editor = self.query_one("#playground-editor", TextArea)
        if self._active_upper_view == "playground":
            try:
                playground_path.write_text(editor.text, encoding="utf-8")
            except Exception:
                pass
            self.current_file = playground_path
            self.execute_script(playground_path)
        else:
            self.action_run_selected()

    def action_run_selected(self) -> None:
        if self.current_file and self.current_file.exists():
            if self._is_playground(self.current_file):
                self.action_save_and_run_playground()
            elif self.current_file.suffix == ".py":
                self.load_code_preview(self.current_file)
                self.execute_script(self.current_file)
            elif self.current_file.suffix == ".md":
                self.load_markdown_preview(self.current_file)
        else:
            self.query_one("#status-bar", Static).update(
                "⚠️ [bold yellow]Selecciona primero un archivo .py o .md en el panel izquierdo.[/]"
            )

    def action_open_playground(self) -> None:
        playground_path = self.base_dir / "playground.py"
        if not playground_path.exists():
            playground_path.write_text('print("Hola mundo")\n', encoding="utf-8")
        self.current_file = playground_path
        self.open_playground_editor(playground_path, focus_editor=True)
        self.execute_script(playground_path)

    def action_practice_mode(self) -> None:
        if not self.current_file or self.current_file.suffix != ".py":
            self.query_one("#status-bar", Static).update(
                "⚠️ [bold yellow]Selecciona un archivo de kata .py para activar el Modo Práctica.[/]"
            )
            return
        if self._is_playground(self.current_file):
            self.query_one("#status-bar", Static).update(
                "🧪 [bold yellow]playground.py ya es un editor libre en vivo. Escribe directamente arriba y presiona Ctrl+R.[/]"
            )
            return
        count = self.solution_mgr.enable_practice_mode(self.current_file)
        self.load_code_preview(self.current_file)
        self.execute_script(self.current_file)
        self.query_one("#status-bar", Static).update(
            f"🎯 [bold magenta]Modo Práctica activado:[/] {count} ejercicios vaciados en "
            f"[bold white]{self.current_file.name}[/]. ¡Ábrelo en tu editor y resuélvelos sin IA!"
        )

    def action_show_hints(self) -> None:
        if not self.current_file or self.current_file.suffix != ".py":
            self.query_one("#status-bar", Static).update(
                "⚠️ [bold yellow]Selecciona un archivo de kata .py para ver su guía de sintaxis y pistas.[/]"
            )
            return
        guide_text = self.solution_mgr.extract_study_guide_and_hints(self.current_file)
        preview_box = self._show_readonly_preview()
        preview_box.clear()
        preview_box.border_title = f"💡 Guía de Sintaxis y Pistas (Sin Spoilers): {self.current_file.name}"
        preview_box.write(Syntax(guide_text, "markdown", theme="monokai", word_wrap=True))
        self.query_one("#status-bar", Static).update(
            f"💡 Mostrando Guía de Sintaxis y Pistas de [bold cyan]{self.current_file.name}[/] (Presiona 'R' para volver al código)"
        )

    def action_peek_solutions(self) -> None:
        if not self.current_file or self.current_file.suffix != ".py":
            self.query_one("#status-bar", Static).update(
                "⚠️ [bold yellow]Selecciona un archivo de kata .py para espiar la solución de referencia.[/]"
            )
            return
        ref_code = self.solution_mgr.get_reference_code(self.current_file)
        self.load_code_preview(self.current_file, custom_code=ref_code, title_prefix="👁️ Solución de Referencia")
        self.query_one("#status-bar", Static).update(
            f"👁️ [bold yellow]Espiando solución oficial de {self.current_file.name}[/] (Tu archivo en disco NO fue sobrescrito)"
        )

    def action_restore_solutions(self) -> None:
        if not self.current_file or self.current_file.suffix != ".py":
            self.query_one("#status-bar", Static).update(
                "⚠️ [bold yellow]Selecciona un archivo de kata .py para restaurar sus soluciones.[/]"
            )
            return
        ok, count = self.solution_mgr.restore_solutions(self.current_file)
        if ok:
            self.load_code_preview(self.current_file)
            self.execute_script(self.current_file)
            self.query_one("#status-bar", Static).update(
                f"♻️ [bold green]Soluciones oficiales restauradas ({count} bloques) en {self.current_file.name}[/]"
            )
        else:
            self.query_one("#status-bar", Static).update(
                "ℹ️ [bold cyan]El archivo ya contiene las soluciones originales.[/]"
            )

    @work(exclusive=True, thread=True)
    def action_run_all_audit(self) -> None:
        output_box = self.query_one("#output-box", RichLog)
        status_bar = self.query_one("#status-bar", Static)
        self.call_from_thread(self._ensure_console_visible)
        self.call_from_thread(output_box.clear)
        self.call_from_thread(
            status_bar.update,
            "⏳ [bold cyan]Ejecutando auditoría global de todos los módulos Python...[/]",
        )

        kata_files = sorted(PYTHON_DIR.rglob("[0-9][0-9]_*.py"))
        table = Table(title="📊 AUDITORÍA GLOBAL DE KATAS PYTHON", expand=True)
        table.add_column("Módulo", style="cyan")
        table.add_column("Kata", style="white")
        table.add_column("Modo", justify="center")
        table.add_column("Estado", justify="center")
        table.add_column("Tiempo", justify="right", style="yellow")

        passed_count = 0
        practice_count = 0
        failed_count = 0
        total_ms = 0.0

        for fpath in kata_files:
            in_practice, pending, total = self.solution_mgr.is_in_practice_mode(fpath)
            t0 = time.perf_counter()
            proc = subprocess.run(
                [sys.executable, str(fpath)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(PROJECT_ROOT),
                env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
            )
            dt_ms = (time.perf_counter() - t0) * 1000
            total_ms += dt_ms

            mod_name = fpath.parent.name
            mode_str = f"🎯 Práctica ({total - pending}/{total})" if in_practice else "📚 Estudio"
            if proc.returncode == 0:
                passed_count += 1
                state_str = "[bold green]✅ PASS[/]"
            elif in_practice:
                practice_count += 1
                state_str = "[bold magenta]⏳ PENDIENTE[/]"
            else:
                failed_count += 1
                state_str = "[bold red]❌ FAIL[/]"

            table.add_row(mod_name, fpath.name, mode_str, state_str, f"{dt_ms:.1f} ms")

        self.call_from_thread(output_box.write, table)
        summary = (
            f"📊 Total: [bold white]{len(kata_files)} katas[/]  |  "
            f"✅ [bold green]{passed_count} Passed[/]  |  "
            f"🎯 [bold magenta]{practice_count} En Práctica[/]  |  "
            f"❌ [bold red]{failed_count} Failed[/]  |  "
            f"⏱️ [bold yellow]{total_ms:.0f} ms[/]"
        )
        self.call_from_thread(status_bar.update, summary)

    def run_syntax_search_in_console(self, query: str) -> None:
        self._ensure_console_visible()
        output_box = self.query_one("#output-box", RichLog)
        output_box.clear()
        table = build_search_results_table(query)
        output_box.write(table)

    def action_clear_output(self) -> None:
        self.query_one("#output-box", RichLog).clear()


def build_search_results_table(query: str) -> Table:
    """Busca un concepto o sintaxis en todos los manuales .md y katas .py y construye una tabla Rich."""
    q = query.lower().strip()
    table = Table(title=f"🔍 Resultados de Búsqueda para: '{query}'", expand=True)
    table.add_column("Archivo", style="bold cyan", no_wrap=True)
    table.add_column("Línea", style="yellow", justify="right")
    table.add_column("Coincidencia / Sintaxis", style="white")

    search_roots = [PYTHON_DIR, NOTES_DIR]
    matches_found = 0
    for root in search_roots:
        if not root.exists():
            continue
        for fpath in sorted(root.rglob("*")):
            if not fpath.is_file() or fpath.suffix not in (".py", ".md"):
                continue
            if any(part.startswith((".", "__")) for part in fpath.parts):
                continue
            try:
                lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue

            rel = fpath.relative_to(PROJECT_ROOT).as_posix()
            file_hits = 0
            for lineno, line in enumerate(lines, start=1):
                if q in line.lower():
                    snippet = line.strip()
                    if len(snippet) > 100:
                        snippet = snippet[:97] + "..."
                    table.add_row(rel, str(lineno), snippet)
                    matches_found += 1
                    file_hits += 1
                    if file_hits >= 4:
                        break
            if matches_found >= 60:
                break

    if matches_found == 0:
        table.add_row("-", "-", f"No se encontraron coincidencias para '{query}'.")
    return table


def run_cli_audit(console: Console, solution_mgr: KataSolutionManager) -> int:
    kata_files = sorted(PYTHON_DIR.rglob("[0-9][0-9]_*.py"))
    table = Table(title="⚡ DEV-KATAS — AUDITORÍA GLOBAL DEL CURRÍCULO PYTHON", expand=True)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Módulo", style="cyan")
    table.add_column("Archivo Kata", style="white")
    table.add_column("Modo", justify="center")
    table.add_column("Resultado", justify="center")
    table.add_column("Tiempo", justify="right", style="yellow")

    passed = 0
    pending_files = 0
    failed = 0
    t_start = time.perf_counter()

    for idx, fpath in enumerate(kata_files, start=1):
        solution_mgr.ensure_backup(fpath)
        in_practice, pending, total = solution_mgr.is_in_practice_mode(fpath)
        t0 = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(fpath)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(PROJECT_ROOT),
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        dt_ms = (time.perf_counter() - t0) * 1000
        mode_str = f"🎯 Práctica ({total - pending}/{total})" if in_practice else f"📚 Estudio ({total}/{total})"

        if proc.returncode == 0:
            passed += 1
            res_str = "[bold green]✅ PASS[/]"
        elif in_practice:
            pending_files += 1
            res_str = "[bold magenta]⏳ PENDIENTE[/]"
        else:
            failed += 1
            res_str = "[bold red]❌ FAIL[/]"

        table.add_row(str(idx), fpath.parent.name, fpath.name, mode_str, res_str, f"{dt_ms:.1f} ms")

    total_ms = (time.perf_counter() - t_start) * 1000
    console.print(table)
    console.print(
        Panel(
            f"📦 Total Katas: [bold]{len(kata_files)}[/]   |   "
            f"✅ Passed: [bold green]{passed}[/]   |   "
            f"🎯 En Práctica: [bold magenta]{pending_files}[/]   |   "
            f"❌ Failed: [bold red]{failed}[/]   |   "
            f"⏱️ Tiempo Total: [bold yellow]{total_ms:.0f} ms[/]",
            border_style="green" if failed == 0 else "red",
        )
    )
    return 0 if failed == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="⚡ DEV-KATAS PYTHON STUDIO — TUI Interactiva, Buscador de Sintaxis y Runner de Práctica Deliberada."
    )
    parser.add_argument(
        "-s",
        "--search",
        type=str,
        help="Busca cualquier sintaxis, método o patrón en las guías y katas (ej: --search heapq)",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Ejecuta la auditoría global de todos los katas de Python en consola.",
    )
    parser.add_argument(
        "-p",
        "--practice",
        type=str,
        help="Activa el Modo Práctica (vacía soluciones con TODO) en un archivo o en 'all'.",
    )
    parser.add_argument(
        "-r",
        "--restore",
        type=str,
        help="Restaura las soluciones oficiales desde la caché en un archivo o en 'all'.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    console = Console()
    solution_mgr = KataSolutionManager(root_dir=PROJECT_ROOT)

    if args.search:
        console.print(build_search_results_table(args.search))
        return

    if args.practice:
        targets = (
            sorted(PYTHON_DIR.rglob("[0-9][0-9]_*.py"))
            if args.practice.lower() == "all"
            else [Path(args.practice).resolve()]
        )
        total_blocks = 0
        for t in targets:
            if t.exists() and t.suffix == ".py":
                total_blocks += solution_mgr.enable_practice_mode(t)
        console.print(
            f"🎯 [bold magenta]Modo Práctica activado[/] en {len(targets)} archivo(s) ({total_blocks} ejercicios listos para resolver sin IA)."
        )
        return

    if args.restore:
        targets = (
            sorted(PYTHON_DIR.rglob("[0-9][0-9]_*.py"))
            if args.restore.lower() == "all"
            else [Path(args.restore).resolve()]
        )
        restored_files = 0
        for t in targets:
            if t.exists() and t.suffix == ".py":
                ok, _ = solution_mgr.restore_solutions(t)
                if ok:
                    restored_files += 1
        console.print(f"♻️ [bold green]Soluciones oficiales restauradas[/] en {restored_files} archivo(s).")
        return

    if args.test:
        sys.exit(run_cli_audit(console, solution_mgr))

    if not PYTHON_DIR.exists():
        console.print(f"[bold red]Error:[/] No se encontró el directorio {PYTHON_DIR}")
        sys.exit(1)

    app = KataRunnerApp(base_dir=PYTHON_DIR)
    app.run()


if __name__ == "__main__":
    main()
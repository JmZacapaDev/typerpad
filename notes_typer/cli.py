# notes_typer/cli.py

"""
Notes Typer CLI

A global CLI tool to manage notes with title, body, optional tags, and timestamps.
Uses Typer for CLI structure and Rich for pretty output.
Stores notes in a SQLite database in the OS-standard user data directory.
ASCII-only display.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from appdirs import user_data_dir
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# -------------------------
# CLI setup
# -------------------------
app = typer.Typer(help="Notes CLI - manage your notes with title, body, tags, and timestamps")
console = Console()

# -------------------------
# Data setup (SQLite)
# -------------------------
APP_NAME = "typerpad"
APP_AUTHOR = "JmZacapa"

DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "notes.db"

engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Note(Base):
    """SQLAlchemy model for a Note."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    tag = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


# -------------------------
# CLI commands
# -------------------------
@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the note"),
    text: str = typer.Argument(..., help="Body text of the note"),
    tag: Optional[str] = typer.Option(None, help="Optional tag"),
):
    """Add a new note with title and body."""
    session = SessionLocal()
    note = Note(title=title, text=text, tag=tag, created_at=datetime.now())
    session.add(note)
    session.commit()
    console.print(Panel(f"Note added (id={note.id})", style="green", title_align="left"))
    session.close()


@app.command()
def list(tag: Optional[str] = typer.Option(None, help="Filter notes by tag")):
    """List all notes, optionally filtered by tag."""
    session = SessionLocal()
    query = session.query(Note)
    if tag:
        query = query.filter(Note.tag == tag)
    notes = query.order_by(Note.id).all()

    if not notes:
        console.print(f"No notes found{f' with tag {tag}' if tag else ''}.", style="yellow")
        session.close()
        raise typer.Exit()

    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Text", style="white")
    table.add_column("Tag", style="green")
    table.add_column("Created At", style="yellow")

    for note in notes:
        table.add_row(
            str(note.id),
            note.title,
            note.text,
            note.tag or "-",
            note.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    console.print(Panel(table, title="Notes", title_align="left"))
    console.print(f"Total notes shown: {len(notes)}", style="blue")
    session.close()


@app.command()
def search(query: str):
    """Search notes by a keyword in title or text."""
    session = SessionLocal()
    notes = session.query(Note).filter(
        (Note.title.ilike(f"%{query}%")) | (Note.text.ilike(f"%{query}%"))
    ).all()

    if not notes:
        console.print(f"No notes found containing '{query}'", style="yellow")
        session.close()
        raise typer.Exit()

    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Text", style="white")
    table.add_column("Tag", style="green")
    table.add_column("Created At", style="yellow")

    for note in notes:
        table.add_row(
            str(note.id),
            note.title,
            note.text,
            note.tag or "-",
            note.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

    console.print(Panel(table, title=f"Search results for '{query}'", title_align="left"))
    console.print(f"Found {len(notes)} notes matching '{query}'", style="blue")
    session.close()


@app.command()
def delete(note_id: int):
    """Delete a note by its ID."""
    session = SessionLocal()
    note = session.query(Note).filter(Note.id == note_id).first()
    if not note:
        console.print(f"Note with id {note_id} not found.", style="red")
        session.close()
        raise typer.Exit()

    session.delete(note)
    session.commit()
    console.print(Panel(f"Note {note_id} deleted", style="red", title_align="left"))
    session.close()


if __name__ == "__main__":
    app()


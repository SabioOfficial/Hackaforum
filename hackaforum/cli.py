import json
import os
import click
from rich.console import Console
from rich.table import Table

DB_FILE = os.path.expanduser("~/.hackaforum/db.json")
console = Console()

def load_db():
    if not os.path.exists(DB_FILE):
        return {"posts": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)
    
def save_db(db):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

@click.group()
def cli():
    """Hackaforum - a CLI forum for Hack Club!"""

@cli.command()
def list():
    """List recent posts woah"""
    db = load_db()
    if not db["posts"]:
        console.print("[yellow]No posts yet. Use 'hackaforum new' to create one![/yellow]")
        return
    table = Table(title="Hackaforum Posts")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="bold")
    table.add_column("Replies", justify="right")
    for i, post in enumerate(db["posts"]):
        table.add_row(str(i), post["title"], str(len(post["replies"])))
    console.print(table)

@cli.command()
@click.argument("post_id", type=int)
def view(post_id):
    """view a post and its replies omg shocking"""
    db = load_db()
    try:
        post = db["posts"][post_id]
        console.rule(f"[bold cyan]{post['title']}")
        console.print(post["body"])
        console.rule("Replies")
        for i, reply in enumerate(post["replies"]):
            console.print(f"[{i}] {reply}")
    except IndexError:
        console.print("[red]Post not found![/red]")

@cli.command()
@click.argument("title")
@click.argument("body")
def new(title, body):
    """creation of a god... a post..."""
    db = load_db()
    db["posts"].append({"title": title, "body": body, "replies": []})
    save_db(db)
    console.print(f"[green]Post '{title}' created![/green]")

@cli.command()
@click.argument("post_id", type=int)
@click.argument("message")
def reply(post_id, message):
    """reply to a post :shocked:"""
    db = load_db()
    try:
        db["posts"][post_id]["replies"].append(message)
        save_db(db)
        console.print("[green]Reply added![/green]")
    except IndexError:
        console.print("[red]Post not found![/red]")
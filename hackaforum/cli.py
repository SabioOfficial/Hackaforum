import json
import os
import click
from rich.console import Console
from rich.table import Table

DB_FILE = os.path.expanduser("~/.hackaforum/db.json")
console = Console()

CATEGORIES = [
    "Meta",
    "Confessions",
    "Resources",
    "Showcase",
    "Help",
    "Events",
    "Shitposts",
    "Miscellaneous",
]

def load_db():
    if not os.path.exists(DB_FILE):
        return {"posts": []}
    
    with open(DB_FILE, "r") as f:
        db = json.load(f)

    migrated = False
    for post in db.get("posts", []):
        if "category" not in post:
            post["category"] = "Miscellaneous"
            migrated = True
        if "replies" not in post:
            post["replies"] = []
            migrated = True
        if "content" not in post and "body" in post:
            post["content"] = post["body"]
            migrated = True

    if migrated:
        save_db(db)

    return db
    
def save_db(db):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

@click.group()
def cli():
    """Hackaforum - a CLI forum for Hack Club!"""
    pass

@cli.command()
def categories():
    """List avilable categories"""
    table = Table(title="Available Categories")
    table.add_column("ID", style="cyan")
    table.add_column("Category", style="green")

    for idx, cat in enumerate(CATEGORIES, 1):
        table.add_row(str(idx), cat)

    console.print(table)

# --------
# 26/08/25  Initial Viewing! (hackaforum view POST_ID)
# 26/08/25  Changed Syntax! (hackaforum view --category CATEGORY_NAME)
# 26/08/25  Restored Specific Post viewing, but you can still view a specific categories' posts! (hackaforum view --category CATEGORY_NAME + hackaforum view POST_ID)
# --------

@cli.command()
@click.argument("post_id", required=False, type=int)
@click.option("--category", type=click.Choice(CATEGORIES), help="Category to view")
def view(post_id, category):
    """view a categories' posts OR a single post by ID and its replies omg shocking"""
    db = load_db()

    if category:
        posts = [(i, p) for i, p in enumerate(db["posts"]) if p["category"] == category]
        if not posts:
            console.print(f"[yellow]No posts found in {category}[/]")
            return
        
        table = Table(title=f"Posts in {category}")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="bold")
        table.add_column("Replies", style="magenta")

        for i, post in posts:
            table.add_row(str(i), post["title"], str(len(post["replies"])))

        console.print(table)
        return
    
    if post_id is not None:
        try:
            post = db["posts"][post_id]
            console.rule(f"[bold cyan]{post['title']}[/] [dim](in {post['category']})[/]")
            console.print(post["content"])
            console.rule("Replies")
            if not post["replies"]:
                console.print("[dim]No replies yet[/]")
            else:
                for i, reply in enumerate(post["replies"]):
                    console.print(f"[{i}] {reply}")
        except IndexError:
            console.print("[red]Post not found![/red]")
        return

    console.print("[red]You must provide either --category or POST_ID[/red]")

# --------
# 26/08/25  Initial Posting! (hackaforum new "Title" "Body")
# 26/08/25  Changed Syntax! (hackaforum post --category CATEGORY_NAME --title "TITLE" --content "CONTENT")
# 26/08/25  Re-add replies i forgot about it oops
# --------

@cli.command()
@click.option("--category", type=click.Choice(CATEGORIES), required=True, help="Category for the post")
@click.option("--title", prompt="Post title", help="Title of your post")
@click.option("--content", prompt="Post content", help="Content of your post")
def post(category, title, content):
    """creation of a god... a post..."""
    db = load_db()
    db["posts"].append({
        "category": category,
        "title": title,
        "content": content,
        "replies": []
    })
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
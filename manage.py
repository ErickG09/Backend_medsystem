import click
from flask.cli import with_appcontext
from app import create_app
from app.extensions import db

app = create_app()

@app.cli.command("ping-db")
@with_appcontext
def ping_db():
    from sqlalchemy import text
    try:
        db.session.execute(text("SELECT 1"))
        click.echo("DB OK")
    except Exception as e:
        click.echo(f"DB ERROR: {e}", err=True)
        raise SystemExit(1)

@app.cli.command("create-admin")
@with_appcontext
def create_admin():
    """Crea un superusuario admin interactivo."""
    from app.models.user import User, UserRole
    from app.security import hash_password, password_is_strong

    first_name = click.prompt("Nombre", type=str)
    last_name = click.prompt("Apellidos", type=str)
    email = click.prompt("Email", type=str)
    username = click.prompt("Usuario", type=str)

    while True:
        password = click.prompt("Contraseña (min 12 chars, Aa1!)", hide_input=True)
        if password_is_strong(password):
            break
        click.echo("Contraseña no cumple política. Intenta de nuevo.", err=True)

    u = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email.lower().strip(),
        username=username.strip(),
        password_hash=hash_password(password),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.session.add(u)
    db.session.commit()
    click.echo(f"Admin creado: {u.id} ({u.username})")

from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import click

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
# initialize the app with the extension
db.init_app(app)

class Lot(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    capacity: Mapped[int] = mapped_column()
    occupancy: Mapped[int] = mapped_column(default=0)

    @property
    def available(self) -> int:
        return self.capacity - self.occupancy

    def __repr__(self) -> str:
        return f"<Lot {self.name} | {self.available} free / {self.capacity}>"
    
# ───────────────────────────────────────────────
# 4. CLI commands
# ───────────────────────────────────────────────

@app.cli.command("init-db")
def init_db_command():
    """Create all tables (if they don't exist)."""
    with app.app_context():
        db.create_all()
    click.echo("Database initialized.")


@app.cli.command("seed-lots")
@click.option("--reset", is_flag=True, help="Delete all existing lots first")
def seed_lots_command(reset):
    """Add initial parking lots (skips duplicates unless --reset used)."""
    with app.app_context():
        if reset:
            Lot.query.delete()
            db.session.commit()
            click.echo("All existing lots deleted.")

        # Your known lots — edit names/capacities as needed
        initial_lots = [
            {"name": "FFH, CTC Lots G9-G16",    "capacity": 750},
            {"name": "CCH, I2C Lot G5",         "capacity": 500},
            {"name": "Intermodal Facility",     "capacity": 450},
            {"name": "West Lot 27",             "capacity": 300},
            {"name": "East Lot 10",             "capacity": 180},
            {"name": "OKT Lot T40",             "capacity": 150},
            {"name": "North Lot 5",             "capacity": 120},
            {"name": "South Engineering Lot",   "capacity": 200},
            {"name": "Union Center Lot 3",      "capacity":  90},
            {"name": "SST West Entrance",       "capacity":   5}, # its 5 i literally counted
        ]

        added = 0
        for data in initial_lots:
            # Check if lot with this name already exists
            exists = db.session.execute(
                db.select(Lot).filter_by(name=data["name"])
            ).scalar_one_or_none()

            if not exists:
                lot = Lot(
                    name=data["name"],
                    capacity=data["capacity"],
                    occupancy=0
                )
                db.session.add(lot)
                added += 1

        db.session.commit()
        click.echo(f"Seed complete. Added {added} new lots.")

@app.route("/")
@app.route("/dashboard")
def dashboard():
    # Fetch all lots, sorted by name
    lots = db.session.execute(
        db.select(Lot).order_by(Lot.name)
    ).scalars().all()

    return render_template(
        "lots_dashboard.html",
        lots=lots,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route("/api/lots")
def api_lots():
    lots = db.session.execute(
        db.select(Lot).order_by(Lot.name)
    ).scalars().all()
    
    # Return JSON data (easy for JS to consume)
    data = [{
        "id": lot.id,
        "name": lot.name,
        "capacity": lot.capacity,
        "occupancy": lot.occupancy,
        "available": lot.available,
        "percent": round((lot.occupancy / lot.capacity * 100) if lot.capacity > 0 else 0)
    } for lot in lots]
    
    return jsonify({
        "lots": data,
        "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

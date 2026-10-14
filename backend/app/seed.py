"""Seed the database with a set of LLD practice problems.

Run this module directly to (re)populate the problems table.
"""

from .database import SessionLocal, Base, engine
from .models import Problem

# A focused set of classic LLD problems. Each has clear requirements and
# evaluation criteria so the feedback engine can give meaningful signals.
PROBLEMS = [
    {
        "title": "Design a Parking Lot",
        "slug": "parking-lot",
        "difficulty": "medium",
        "short_description": "Design a parking lot system that manages spots, vehicles, and ticketing.",
        "description": (
            "Design a parking lot for a multi-floor building. Vehicles of different "
            "types (car, motorcycle, truck) enter, take a ticket, park in an "
            "available spot, and pay on exit. The system should track spot "
            "occupancy and handle different spot sizes."
        ),
        "requirements": """Support vehicle types: motorcycle, car, truck.
Each floor has spots of different sizes.
A vehicle is assigned to the smallest spot that fits it.
Issue a ticket on entry; compute parking fee on exit.
Support multiple floors.
Keep the system extensible for new vehicle types or pricing rules.""",
        "hints": """Think about a Vehicle hierarchy and a Spot hierarchy.
Use composition: ParkingLot has many Floor, Floor has many Spot.
A Ticket links a Vehicle to a Spot and entry time.
Consider a strategy pattern for pricing.""",
        "evaluation_criteria": """Clear separation of Vehicle, Spot, Floor, ParkingLot, Ticket responsibilities.
Proper abstraction for spot assignment and pricing.
Relationships between classes are explicit.
Extensibility for new vehicle types and pricing rules.""",
    },
    {
        "title": "Design an Elevator System",
        "slug": "elevator-system",
        "difficulty": "hard",
        "short_description": "Design an elevator control system for a building with multiple elevators.",
        "description": (
            "Design the control software for a bank of elevators in a building. "
            "Users press buttons inside and outside elevators. The system "
            "schedules which elevator serves which request and moves elevators "
            "efficiently between floors."
        ),
        "requirements": """Multiple elevators, multiple floors.
Handle external requests (hall buttons) and internal requests (car buttons).
Dispatch the most appropriate elevator to each external request.
Elevators move floor by floor, stopping at requested floors.
Support idle state and direction (up/down/idle).
Keep the scheduling strategy pluggable.""",
        "hints": """Model Elevator, Request, and a Scheduler/ElevatorController.
Separate the state of each elevator from the dispatch logic.
Think about an ElevatorState with current floor, direction, and pending requests.
The scheduler could use SCAN or LOOK algorithm patterns.""",
        "evaluation_criteria": """Separation of Elevator state from Scheduling logic.
Clear handling of request types (internal vs external).
Pluggable scheduling strategy (open/closed principle).
State transitions (idle, moving up, moving down) are well defined.""",
    },
    {
        "title": "Design a Vending Machine",
        "slug": "vending-machine",
        "difficulty": "easy",
        "short_description": "Design a vending machine that accepts coins, selects products, and dispenses them.",
        "description": (
            "Design a vending machine. A user inserts coins, selects a product, "
            "and the machine dispenses it if enough money was inserted and the "
            "product is in stock. The machine returns change if needed."
        ),
        "requirements": """Accept coins of different denominations.
Display the current inserted amount.
Allow product selection and check stock.
Dispense product and return change if overpaid.
Return inserted coins if cancelled.
Handle insufficient funds and out-of-stock gracefully.""",
        "hints": """Use a state machine: Idle, HasMoney, Dispensing.
Model Product, Inventory, and Coin/Payment separately.
A State pattern can cleanly model the machine's behaviour.""",
        "evaluation_criteria": """State transitions are clearly modelled.
Separation of inventory, payment, and product concerns.
Edge cases (out of stock, insufficient funds, cancel) are handled.
The design is readable and testable.""",
    },
    {
        "title": "Design a Snake Game",
        "slug": "snake-game",
        "difficulty": "medium",
        "short_description": "Design the logic for the classic Snake game with board, snake, and food.",
        "description": (
            "Design the core logic of a Snake game. The snake moves on a grid, "
            "eats food to grow, and ends the game if it hits a wall or itself. "
            "The game keeps score and supports restarting."
        ),
        "requirements": """A grid-based board.
Snake grows when it eats food.
New food appears at a random empty cell after eating.
Game over on wall collision or self collision.
Track and update score.
Decouple game logic from rendering.""",
        "hints": """Model Cell, Snake, Food, Board, and Game.
The Snake holds a list of cells (head first).
Game orchestrates the tick: move snake, check collisions, handle food.
Keep rendering out of the domain so the logic is testable.""",
        "evaluation_criteria": """Clear separation of Board, Snake, Food, and Game responsibilities.
Collision detection is encapsulated.
Game loop logic is testable without a UI.
Extensible to new rules (e.g., obstacles, power-ups).""",
    },
]


def seed() -> None:
    """Create tables and insert the seed problems (idempotent)."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Idempotency: skip if problems already exist.
        existing = db.query(Problem).count()
        if existing > 0:
            print(f"Database already has {existing} problems; skipping seed.")
            return

        for p in PROBLEMS:
            db.add(Problem(**p))
        db.commit()
        print(f"Seeded {len(PROBLEMS)} problems.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

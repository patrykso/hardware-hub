from datetime import datetime, date, timezone
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
from sqlalchemy.orm import Session

from database import SessionLocal, Equipment, Rental, User

# Initialize FastMCP Server
mcp = FastMCP("Hub Rental Server")

# Business Logic Threshold Constants (as required by AGENTS.md)
LONG_IN_REPAIR_THRESHOLD_DAYS = 30
HIGH_RENTAL_FREQUENCY_THRESHOLD = 10
LONG_ACTIVE_RENTAL_THRESHOLD_DAYS = 14


def make_naive(dt: Any) -> datetime:
    """Helper to convert any date or timezone-aware datetime to a naive UTC datetime."""
    if dt is None:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime(dt.year, dt.month, dt.day)
    if dt.tzinfo is not None:
        # Convert to UTC first, then make naive
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.replace(tzinfo=None)
    return dt


@mcp.tool()
def get_inventory() -> List[Dict[str, Any]]:
    """Retrieve all hardware equipment details.
    
    Returns:
        List[Dict[str, Any]]: A list of all equipment items, including id, name, brand,
        purchase_date (ISO format), and current status.
    """
    session: Session = SessionLocal()
    try:
        equipments = session.query(Equipment).all()
        inventory = []
        for eq in equipments:
            inventory.append({
                "id": eq.id,
                "name": eq.name,
                "brand": eq.brand,
                "purchase_date": eq.purchase_date.isoformat() if eq.purchase_date else None,
                "status": eq.status
            })
        return inventory
    finally:
        session.close()


@mcp.tool()
def get_active_rentals() -> List[Dict[str, Any]]:
    """Retrieve all currently active (open) rentals with renter details.
    
    Returns:
        List[Dict[str, Any]]: A list of active rentals containing the rental ID,
        equipment name, renter's username, and rented_at timestamp.
    """
    session: Session = SessionLocal()
    try:
        active_rentals = (
            session.query(Rental)
            .join(Equipment)
            .join(User)
            .filter(Rental.returned_at.is_(None))
            .all()
        )
        
        results = []
        for rental in active_rentals:
            results.append({
                "rental_id": rental.id,
                "equipment_name": rental.equipment.name,
                "username": rental.user.username,
                "rented_at": rental.rented_at.isoformat() if rental.rented_at else None
            })
        return results
    finally:
        session.close()


@mcp.tool()
def get_rental_history(equipment_ids: str) -> List[Dict[str, Any]]:
    """Retrieve the full rental history (completed and active) for one or more equipment items.
    
    Args:
        equipment_ids (str): A comma-separated list of equipment IDs (e.g. "1,2,3") or a single ID (e.g. "1").
        
    Returns:
        List[Dict[str, Any]]: A list of history records, including the equipment_id,
        renter's username, rented_at, and returned_at (None if still active) timestamps.
    """
    session: Session = SessionLocal()
    try:
        # Split by comma and strip spaces, parsing each as an integer
        ids = []
        for part in equipment_ids.split(','):
            part = part.strip()
            if not part:
                continue
            try:
                ids.append(int(part))
            except ValueError:
                # Ignore non-integer elements
                continue
        
        if not ids:
            return []
            
        rentals = (
            session.query(Rental)
            .join(User)
            .filter(Rental.equipment_id.in_(ids))
            .order_by(Rental.rented_at.desc())
            .all()
        )
        
        history = []
        for r in rentals:
            history.append({
                "equipment_id": r.equipment_id,
                "username": r.user.username,
                "rented_at": r.rented_at.isoformat() if r.rented_at else None,
                "returned_at": r.returned_at.isoformat() if r.returned_at else None
            })
        return history
    finally:
        session.close()


@mcp.tool()
def audit_inventory() -> List[Dict[str, Any]]:
    """Apply deterministic business logic to identify issues/findings across the entire inventory.
    
    Flags four types of issues:
      - long_in_repair: Status is 'Repair' and no rental/purchase activity for > 30 days. Severity: warning.
      - never_rented: No rental records exist at all. Severity: info.
      - high_rental_frequency: Completed rentals count > 10. Severity: info.
      - long_active_rental: Open rental has been active for > 14 days. Severity: warning.
      
    Returns:
        List[Dict[str, Any]]: Structured list of findings. If no issues, returns an empty list.
    """
    session: Session = SessionLocal()
    try:
        equipments = session.query(Equipment).all()
        findings = []
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        
        for eq in equipments:
            # Query all rentals for this item
            rentals = session.query(Rental).filter(Rental.equipment_id == eq.id).all()
            
            # Check 1: never_rented
            if len(rentals) == 0:
                findings.append({
                    "equipment_id": eq.id,
                    "name": eq.name,
                    "issue_type": "never_rented",
                    "detail": "Equipment has never been rented.",
                    "severity": "info"
                })
            
            # Check 2: long_in_repair
            if eq.status == "Repair":
                # Find the latest rental activity
                latest_activity = None
                for r in rentals:
                    act = r.returned_at or r.rented_at
                    if act:
                        act_naive = make_naive(act)
                        if latest_activity is None or act_naive > latest_activity:
                            latest_activity = act_naive
                
                # Fallback to purchase date if never rented
                if latest_activity is None and eq.purchase_date:
                    latest_activity = make_naive(eq.purchase_date)
                
                if latest_activity:
                    days_inactive = (now_naive - latest_activity).days
                    if days_inactive > LONG_IN_REPAIR_THRESHOLD_DAYS:
                        findings.append({
                            "equipment_id": eq.id,
                            "name": eq.name,
                            "issue_type": "long_in_repair",
                            "detail": f"In Repair for {days_inactive} days with no rental activity.",
                            "severity": "warning"
                        })
            
            # Check 3: high_rental_frequency
            completed_rentals = [r for r in rentals if r.returned_at is not None]
            if len(completed_rentals) > HIGH_RENTAL_FREQUENCY_THRESHOLD:
                findings.append({
                    "equipment_id": eq.id,
                    "name": eq.name,
                    "issue_type": "high_rental_frequency",
                    "detail": f"High rental frequency: {len(completed_rentals)} completed rentals.",
                    "severity": "info"
                })
                
            # Check 4: long_active_rental
            active_rental = next((r for r in rentals if r.returned_at is None), None)
            if active_rental:
                rented_naive = make_naive(active_rental.rented_at)
                days_active = (now_naive - rented_naive).days
                if days_active > LONG_ACTIVE_RENTAL_THRESHOLD_DAYS:
                    findings.append({
                        "equipment_id": eq.id,
                        "name": eq.name,
                        "issue_type": "long_active_rental",
                        "detail": f"Active rental open for {days_active} days.",
                        "severity": "warning"
                    })
                    
        return findings
    finally:
        session.close()


if __name__ == "__main__":
    mcp.run()

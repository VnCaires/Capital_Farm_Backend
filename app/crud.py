from sqlalchemy.orm import Session

from . import auth, models


def get_player_by_username(db: Session, username: str) -> models.Player | None:
    return db.query(models.Player).filter(models.Player.username == username).first()


def create_player(db: Session, username: str, password: str) -> models.Player:
    hashed_password = auth.hash_password(password)
    db_player = models.Player(
        username=username,
        hashed_password=hashed_password
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def deposit_balance(db: Session, player: models.Player, amount: float) -> models.Player:
    player.balance += amount
    db.commit()
    db.refresh(player)
    return player

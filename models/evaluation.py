from app import db

class Evaluation(db.Model):
    __tablename__ = 'Evaluations' # Match DB table name

    # Define at least a primary key
    id = db.Column(db.Integer, primary_key=True)

    # Other columns can be added later
    player_id = db.Column(db.Integer, db.ForeignKey('Players.id'), nullable=False) # Assuming Players.id
    coach_id = db.Column(db.Integer, db.ForeignKey('Coaches.id'), nullable=False) # Changed target table to Coaches
    game_id = db.Column(db.Integer, db.ForeignKey('Games.id'), nullable=False)
    skill_item = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.Text, nullable=True)

    # Relationships (add back_populates later if needed)
    player = db.relationship('Player')
    coach = db.relationship('Coach') # Changed relationship target
    game = db.relationship('Game')

    def __repr__(self):
        return f'<Evaluation {self.id} for Player:{self.player_id} Skill:{self.skill_item}>'

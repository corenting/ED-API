from api.community_goals.utils import get_community_goals
from flask.blueprints import Blueprint

community_goals_bp = Blueprint("community_goals", __name__)


@community_goals_bp.route("/")
def flask_get_community_goals():
    return get_community_goals()

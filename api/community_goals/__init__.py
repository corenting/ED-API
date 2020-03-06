from api.community_goals.utils import get_community_goals
from flask.blueprints import Blueprint

community_goals_bp = Blueprint("community_goals", __name__)


@community_goals_bp.route("/")
def flask_get_community_goals():
    """Return the latest community goals
    ---
    tags:
      - Community goals
    definitions:
      CommunityGoalError:
        type: object
        properties:
          error:
            type: string
      CommunityGoalResponse:
        type: array
        items:
          type: object
          properties:
            contributors:
              type: integer
            date:
              type: object
              properties:
                end:
                  type: string
                  format: date-time
                last_update:
                  type: string
                  format: date-time
            description:
              type: string
            id:
              type: integer
            location:
              type: object
              properties:
                station:
                  type: string
                system:
                  type: string
            objective:
              type: string
              example: Hand in Bounty Vouchers
            ongoing:
              type: boolean
              description: If the community goal is currently active or finished
            reward:
              type: string
            tier_progress:
              type: object
              properties:
                current:
                  type: integer
                total:
                  type: integer
            title:
              type: string
    responses:
      200:
        description: A list of community goals
        schema:
          $ref: '#/definitions/CommunityGoalResponse'
      500:
        description: Error on fetching goals
        schema:
          $ref: '#/definitions/CommunityGoalError'
    """
    return get_community_goals()

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database.database import SessionLocal
from app.models.models import Feature, UserCredit, CreditUsage, UserActivityLog, User

# def handle_feature_use(user_id: str, feature_name: str, ip_address: str, user_agent: str):
#     db: Session = SessionLocal()
#     try:
#         # Step 1: Find the feature
#         feature = db.query(Feature).filter(Feature.name == feature_name).first()
#         if not feature:
#             return None, "Feature not found."

#         is_free = feature.is_free
#         credit_cost = feature.credit_cost
#         feature_id = feature.id

#         # Step 2: If free
#         if is_free:
#             usage = CreditUsage(
#                 user_id=user_id,
#                 feature_id=feature_id,
#                 credits_used=0,
#                 created_at=datetime.utcnow()
#             )
#             db.add(usage)

#             log = UserActivityLog(
#                 user_id=user_id,
#                 activity_type="feature_use",
#                 feature_id=feature_id,
#                 details=f"Used free feature: {feature_name}",
#                 ip_address=ip_address,
#                 user_agent=user_agent,
#                 created_at=datetime.utcnow()
#             )
#             db.add(log)

#             db.commit()
#             return {"message": f"Free feature '{feature_name}' used successfully."}, None

#         # Step 3: Paid feature — check and deduct credits
#         wallet = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
#         if not wallet:
#             return None, "User wallet not found."

#         if wallet.credits_balance < credit_cost:
#             return None, "Insufficient credits."

#         wallet.credits_balance -= credit_cost
#         wallet.updated_at = func.now()

#         usage = CreditUsage(
#             user_id=user_id,
#             feature_id=feature_id,
#             credits_used=credit_cost,
#             created_at=datetime.utcnow()
#         )
#         db.add(usage)

#         log = UserActivityLog(
#             user_id=user_id,
#             activity_type="feature_use",
#             feature_id=feature_id,
#             details=f"Used paid feature: {feature_name}",
#             ip_address=ip_address,
#             user_agent=user_agent,
#             created_at=datetime.utcnow()
#         )
#         db.add(log)

#         db.commit()
#         return {
#             "message": f"Paid feature '{feature_name}' used successfully.",
#             "credits_deducted": credit_cost,
#             "remaining_balance": wallet.credits_balance
#         }, None
#     finally:
#         db.close()


def handle_feature_use(user_id: str, feature_name: str, ip_address: str, user_agent: str):
    db: Session = SessionLocal()
    try:
        # Step 1: Fetch user and role
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "User not found."

        is_admin = user.role_level >= 2

        # Step 2: Find the feature
        feature = db.query(Feature).filter(Feature.name == feature_name).first()
        if not feature:
            return None, "Feature not found."

        feature_id = feature.id
        credit_cost = feature.credit_cost if not is_admin else 0  # admin uses for free

        # Step 3: Check credits if not admin and not free feature
        if not is_admin and not feature.is_free:
            wallet = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
            if not wallet:
                return None, "User wallet not found."
            if wallet.credits_balance < feature.credit_cost:
                return None, "Insufficient credits."
            wallet.credits_balance -= feature.credit_cost
            wallet.updated_at = func.now()
            db.commit()

        # Step 4: Log credit usage (even if free or admin)
        usage = CreditUsage(
            user_id=user_id,
            feature_id=feature_id,
            credits_used=credit_cost,
            created_at=datetime.utcnow()
        )
        db.add(usage)

        # Step 5: Log activity
        log = UserActivityLog(
            user_id=user_id,
            activity_type="feature_use",
            feature_id=feature_id,
            details=f"Used feature: {feature_name}",
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        db.add(log)

        db.commit()

        response = {
            "message": f"Feature '{feature_name}' used successfully.",
            "credits_deducted": credit_cost,
        }

        if not is_admin and not feature.is_free:
            response["remaining_balance"] = wallet.credits_balance

        return response, None

    finally:
        db.close()
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from donations.models import Donation
from users.models import UserProfile

from causes.models import Cause


def _fallback_newest_active_cause_ids(top_n=5):
    return list(
        Cause.objects.filter(
            status="ACTIVE",
            organization__verification_status="APPROVED",
        )
        .order_by("-created_at")
        .values_list("id", flat=True)[:top_n]
    )


def get_cause_recommendations(user, top_n=5):
    """Return an ordered list of recommended active cause IDs for a user."""
    try:
        profile = UserProfile.objects.prefetch_related("interests").get(user=user)

        user_interests = list(profile.interests.values_list("name", flat=True))

        recent_donations = (
            Donation.objects.filter(user=user, status="SUCCESS")
            .select_related("cause__category")
            .order_by("-created_at")[:10]
        )
        donated_categories = [
            donation.cause.category.name
            for donation in recent_donations
            if donation.cause and donation.cause.category
        ]

        weighted_profile_terms = user_interests + (donated_categories * 2)
        weighted_profile = " ".join(weighted_profile_terms).strip()
        if not weighted_profile:
            return _fallback_newest_active_cause_ids(top_n=top_n)

        donated_cause_ids = Donation.objects.filter(user=user).values_list("cause_id", flat=True)

        candidate_causes = list(
            Cause.objects.filter(
                status="ACTIVE",
                organization__verification_status="APPROVED",
            )
            .exclude(id__in=donated_cause_ids)
            .select_related("category")
        )
        if not candidate_causes:
            return _fallback_newest_active_cause_ids(top_n=top_n)

        df = pd.DataFrame(
            [
                {
                    "id": cause.id,
                    "text": f"{(cause.category.name if cause.category else '')} {cause.description}",
                }
                for cause in candidate_causes
            ]
        )

        if df.empty:
            return _fallback_newest_active_cause_ids(top_n=top_n)

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(df["text"].tolist() + [weighted_profile])

        user_vector = tfidf_matrix[-1]
        cause_vectors = tfidf_matrix[:-1]
        scores = cosine_similarity(user_vector, cause_vectors).flatten()

        scored = list(zip(df["id"].tolist(), scores))
        scored.sort(key=lambda item: item[1], reverse=True)

        return [cause_id for cause_id, _score in scored[:top_n]]
    except Exception:
        return _fallback_newest_active_cause_ids(top_n=top_n)
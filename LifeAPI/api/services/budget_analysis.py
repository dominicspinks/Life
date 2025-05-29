import re
from collections import Counter
from django.db import transaction

from api.models import (
    BudgetCategoryTermFrequency,
    BudgetTermType,
    BudgetPurchase
)

# Cache term types by word length
TERM_TYPE_CACHE = {}

def get_all_term_types() -> list[BudgetTermType]:
    global TERM_TYPE_CACHE
    if not TERM_TYPE_CACHE:
        TERM_TYPE_CACHE = {
            t.word_length: t for t in BudgetTermType.objects.all()
        }
    return list(TERM_TYPE_CACHE.values())

def tokenize(text: str) -> list[str]:
    # Remove non-word characters
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    tokens = cleaned.split()
    return [t for t in tokens if not any(char.isdigit() for char in t)]

def get_ngrams(tokens: list[str], n: int) -> list[str]:
    if len(tokens) < n:
        return set()
    return {" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}

@transaction.atomic
def update_term_frequencies_from_purchase(purchase: BudgetPurchase):
    if not purchase.description or not purchase.category:
        return

    tokens = tokenize(purchase.description)
    category_id = purchase.category_id

    for term_type in get_all_term_types():
        n = term_type.word_length
        terms = get_ngrams(tokens, n)
        for term in terms:
            _upsert_term_frequency(category_id, term, term_type.id)

def _upsert_term_frequency(category_id: int, term: str, term_type_id: int):
    obj, created = BudgetCategoryTermFrequency.objects.get_or_create(
        category_id=category_id,
        term=term,
        term_type_id=term_type_id,
        defaults={'frequency': 1}
    )
    if not created:
        obj.frequency += 1
        obj.save()

def suggest_category_for_description(description: str, user_module) -> int | None:
    tokens = tokenize(description)
    terms = [t for term_type in get_all_term_types() for t in get_ngrams(tokens, term_type.word_length)]

    # Query all matches for terms in this user module
    matches = BudgetCategoryTermFrequency.objects.filter(
        category__user_module=user_module,
        term__in=terms
    ).select_related('category', 'term_type')

    if not matches:
        return None

    # Map term → list of (category_id, frequency, weight)
    term_to_categories = {}
    for m in matches:
        if m.term not in term_to_categories:
            term_to_categories[m.term] = []
        term_to_categories[m.term].append({
            'category_id': m.category_id,
            'frequency': m.frequency,
            'weight': m.term_type.weight
        })

    # Check if there are enough matches to continue
    total_terms = len(terms)
    matched_terms = len(term_to_categories)

    MIN_MATCH_RATIO = 0.3  # To be tuned over time

    if total_terms == 0 or matched_terms / total_terms < MIN_MATCH_RATIO:
        return None

    category_scores = {}

    # For each term, score all associated categories
    for term, entries in term_to_categories.items():
        num_categories = len(entries)
        term_score = 1 / (num_categories * num_categories)

        for entry in entries:
            category_id = entry['category_id']
            weighted_score = entry['weight'] * term_score
            # print(f"{term},{category_id},{weighted_score},{term_score}")
            # Discard low scoring terms
            if weighted_score > 0.1:
                category_scores[category_id] = category_scores.get(category_id, 0) + weighted_score

    if not category_scores:
        return None

    best_category_id, best_score = max(category_scores.items(), key=lambda item: item[1])
    return best_category_id
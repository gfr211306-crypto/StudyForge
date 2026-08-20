from __future__ import annotations

import html
import math
import re
from collections import Counter, defaultdict

from opencc import OpenCC

from studyforge.cefr import CEFRProfile, default_cefr_profile
from studyforge.dictionary import DictionaryStore
from studyforge.models import PdfDocument, VocabularyItem


LEVEL_LABELS = {
    "balanced": "綜合推薦",
    "basic": "基礎常用",
    "intermediate": "中高階",
    "advanced": "進階挑戰",
    "ielts": "IELTS 單字",
}

TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)?")
SENTENCE_RE = re.compile(r"(?<=[.!?])(?:[\"”’')\]]*)\s+|\n{2,}")

# Function words and high-frequency words that rarely make useful flashcards.
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "also", "am",
    "an", "and", "any", "are", "aren't", "around", "as", "at", "be", "because",
    "been", "before", "being", "below", "between", "both", "but", "by", "can",
    "cannot", "could", "did", "do", "does", "doing", "don't", "down", "during",
    "each", "either", "else", "enough", "especially", "etc", "even", "ever",
    "every", "few", "first", "for", "from", "further", "get", "gets", "getting",
    "got", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "however", "i", "if", "in", "into", "is",
    "isn't", "it", "its", "itself", "just", "least", "less", "like", "likely",
    "made", "make", "many", "may", "me", "might", "more", "most", "much", "must",
    "my", "myself", "neither", "never", "no", "nor", "not", "now", "of", "off",
    "often", "on", "once", "one", "only", "or", "other", "our", "ours",
    "ourselves", "out", "over", "own", "rather", "said", "same", "say", "says",
    "second", "see", "seem", "several", "she", "should", "since", "so", "some",
    "still", "such", "take", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "though",
    "through", "to", "too", "under", "until", "up", "upon", "us", "use", "used",
    "using", "very", "was", "we", "well", "were", "what", "when", "where",
    "whether", "which", "while", "who", "whom", "whose", "why", "will", "with",
    "within", "without", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves",
}

POS_MAP = {
    "n": "名詞",
    "v": "動詞",
    "vt": "及物動詞",
    "vi": "不及物動詞",
    "a": "形容詞",
    "ad": "副詞",
    "adj": "形容詞",
    "r": "副詞",
    "adv": "副詞",
    "prep": "介系詞",
    "conj": "連接詞",
    "pron": "代名詞",
    "num": "數詞",
    "art": "冠詞",
    "int": "感嘆詞",
    "aux": "助動詞",
}

TRADITIONAL_CHINESE = OpenCC("s2twp")


def normalize_token(token: str) -> str:
    token = token.replace("’", "'").lower().strip("'")
    if token.endswith("'s") and len(token) > 4:
        token = token[:-2]
    return token


def _has_ielts_tag(tags: str) -> bool:
    return bool(re.search(r"(?:^|[^a-z])ielts(?:[^a-z]|$)", tags.lower()))


def _format_pos(raw_pos: str, translation: str) -> str:
    supported = r"n|v|vt|vi|a|ad|adj|r|adv|prep|conj|pron|num|art|int|aux"
    translation_pos = re.findall(
        rf"(?:^|\n)({supported})\.",
        translation.lower(),
    )
    raw_matches = re.findall(
        rf"(?:^|[/,\s])({supported})(?=[:./,\s]|$)",
        raw_pos.lower(),
    )
    abbreviations = translation_pos + raw_matches
    cleaned: list[str] = []
    for abbreviation in abbreviations:
        key = abbreviation.strip(" ./,").lower()
        if key in POS_MAP and POS_MAP[key] not in cleaned:
            cleaned.append(POS_MAP[key])
    return "／".join(cleaned[:3]) if cleaned else "其他"


def _clean_translation(translation: str) -> str:
    value = translation.replace("\\n", "；").replace("\n", "；")
    value = re.sub(
        r"(?i)(^|；)\s*(n|v|vt|vi|a|ad|adj|r|adv|prep|conj|pron|num|art|int|aux)\.\s*",
        r"\1",
        value,
    )
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[；;]{2,}", "；", value).strip(" ；;")
    if len(value) > 100:
        value = value[:97].rstrip("；;, ") + "…"
    return TRADITIONAL_CHINESE.convert(value) if value else "請自行補充中文意思"


def _split_sentences(text: str) -> list[str]:
    sentences = []
    for sentence in SENTENCE_RE.split(text):
        cleaned = re.sub(r"\s+", " ", sentence).strip()
        word_count = len(TOKEN_RE.findall(cleaned))
        if 4 <= word_count <= 70:
            sentences.append(cleaned)
    return sentences


def _example_for(
    lemma: str, sentences: list[str], form_to_lemma: dict[str, str]
) -> str:
    best_sentence = ""
    best_score = float("-inf")
    for sentence in sentences:
        tokens = [normalize_token(token) for token in TOKEN_RE.findall(sentence)]
        if not any(form_to_lemma.get(token, token) == lemma for token in tokens):
            continue
        length = len(tokens)
        score = -abs(length - 18)
        if sentence[0:1].isupper():
            score += 2
        if len(sentence) <= 220:
            score += 2
        if score > best_score:
            best_score = score
            best_sentence = sentence
    if not best_sentence:
        return f'The word "{lemma}" is important in this reading.'
    if len(best_sentence) > 260:
        best_sentence = best_sentence[:257].rsplit(" ", 1)[0] + "…"
    return html.unescape(best_sentence)


def _difficulty_rank(frequency_rank: int, bnc_rank: int) -> int:
    ranks = [rank for rank in (frequency_rank, bnc_rank) if rank > 0]
    return min(ranks) if ranks else 25000


def _matches_level(rank: int, level: str) -> bool:
    if level == "basic":
        return rank <= 7000
    if level == "intermediate":
        return 3000 <= rank <= 22000
    if level == "advanced":
        return rank >= 8000
    return True


def analyze_vocabulary(
    document: PdfDocument,
    dictionary: DictionaryStore,
    limit: int = 30,
    level: str = "balanced",
    min_occurrences: int = 1,
    cefr_profile: CEFRProfile | None = None,
) -> list[VocabularyItem]:
    """Rank useful words and enrich them with dictionary and PDF context."""
    profile = cefr_profile or default_cefr_profile()
    page_tokens: list[list[str]] = []
    original_case: dict[str, Counter[str]] = defaultdict(Counter)
    all_forms: list[str] = []

    for page in document.pages:
        forms = []
        for original in TOKEN_RE.findall(page):
            normalized = normalize_token(original)
            if len(normalized) < 3 or normalized in STOPWORDS:
                continue
            if not re.fullmatch(r"[a-z]+(?:['-][a-z]+)*", normalized):
                continue
            forms.append(normalized)
            all_forms.append(normalized)
            original_case[normalized][original] += 1
        page_tokens.append(forms)

    form_to_lemma, entries = dictionary.resolve_many(all_forms)
    lemma_counts: Counter[str] = Counter()
    lemma_pages: dict[str, set[int]] = defaultdict(set)
    lemma_forms: dict[str, Counter[str]] = defaultdict(Counter)

    for page_number, forms in enumerate(page_tokens, start=1):
        for form in forms:
            lemma = form_to_lemma.get(form)
            if not lemma or lemma in STOPWORDS or len(lemma) < 3:
                continue
            lemma_counts[lemma] += 1
            lemma_pages[lemma].add(page_number)
            lemma_forms[lemma][form] += 1

    sentences = _split_sentences(document.full_text)
    candidates: list[VocabularyItem] = []
    for lemma, count in lemma_counts.items():
        if count < min_occurrences:
            continue
        entry = entries.get(lemma)
        if not entry or not entry.translation:
            continue

        rank = _difficulty_rank(entry.frequency_rank, entry.bnc_rank)
        if not _matches_level(rank, level):
            continue

        # Avoid likely names: capitalized almost every time, unless they appear in the dictionary as Oxford words.
        forms = lemma_forms[lemma]
        capitalized = sum(
            occurrence_count
            for form, occurrence_count in forms.items()
            for original, original_count in original_case[form].items()
            if original[:1].isupper()
            for occurrence_count in [min(occurrence_count, original_count)]
        )
        if count >= 2 and capitalized / count > 0.85 and not entry.oxford:
            continue

        page_coverage = len(lemma_pages[lemma]) / max(document.page_count, 1)
        rarity = min(math.log1p(rank) / math.log1p(35000), 1.0)
        academic_bonus = 1.1 if any(
            tag in entry.tags.lower()
            for tag in ("toefl", "ielts", "gre", "cet6", "ky", "academic")
        ) else 0.0
        oxford_bonus = 0.35 if entry.oxford else 0.0
        is_ielts = _has_ielts_tag(entry.tags)
        ielts_bonus = 2.5 if level == "ielts" and is_ielts else 0.0
        score = (
            math.log1p(count) * 3.2
            + page_coverage * 2.4
            + rarity * 1.7
            + min(len(lemma), 12) / 12
            + academic_bonus
            + oxford_bonus
            + ielts_bonus
        )

        candidates.append(
            VocabularyItem(
                word=entry.word,
                phonetic=entry.phonetic,
                part_of_speech=_format_pos(entry.part_of_speech, entry.translation),
                translation=_clean_translation(entry.translation),
                example=_example_for(lemma, sentences, form_to_lemma),
                count=count,
                pages=tuple(sorted(lemma_pages[lemma])),
                score=score,
                cefr_level=profile.level_for(entry.word),
                is_ielts=is_ielts,
            )
        )

    if level == "ielts":
        candidates.sort(
            key=lambda item: (
                not item.is_ielts,
                -item.score,
                -item.count,
                item.word,
            )
        )
    else:
        candidates.sort(key=lambda item: (-item.score, -item.count, item.word))
    return candidates[: max(1, limit)]

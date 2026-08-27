from typing import Any, Dict, List, Optional, Tuple
import re

from rapidfuzz import fuzz

MATCH_THRESHOLD = 70          # raised — was too permissive at 55
MIN_TARGET_WORDS = 3          # below this, content fuzzy-matching is unreliable


def _normalize_number(n: str) -> str:
    """'11 (a)' -> '11a', 'Q3' -> '3', '2.' -> '2' -- for loose anchor comparison."""
    return re.sub(r"[^a-z0-9]", "", n.lower())


def _find_anchor_span(
    visible_number: Optional[str],
    word_boxes: List[Dict[str, Any]],
    span_len: int = 10,
) -> Optional[List[Dict[str, Any]]]:
    """Look for the literal question-number label (e.g. 'Ans 2', '11 (a)') in the
    OCR words, and return that word plus the following span_len words as the
    answer's region. This is far more reliable than fuzzy content matching."""
    if not visible_number:
        return None

    target_norm = _normalize_number(visible_number)
    if not target_norm:
        return None

    n = len(word_boxes)
    for i in range(n):
        # try combining 1-3 consecutive words as a candidate label match
        for span_size in (1, 2, 3):
            if i + span_size > n:
                continue
            combined = "".join(word_boxes[j]["text"] for j in range(i, i + span_size))
            if _normalize_number(combined) == target_norm:
                start = i
                end = min(n, i + span_size + span_len)
                return word_boxes[start:end]
    return None


def _best_window_match(
    target_text: str,
    word_boxes: List[Dict[str, Any]],
    window: int = 8,
) -> Tuple[Optional[List[Dict[str, Any]]], float]:
    target = " ".join(target_text.split()[:12])
    if not target or not word_boxes:
        return None, 0.0
    if len(target.split()) < MIN_TARGET_WORDS:
        return None, 0.0  # too short to trust content-based fuzzy matching

    best_score = 0.0
    best_span = None
    step = max(1, window // 2)
    for i in range(0, len(word_boxes), step):
        span = word_boxes[i:i + window]
        if not span:
            continue
        candidate = " ".join(w["text"] for w in span)
        score = fuzz.partial_ratio(target, candidate)
        if score > best_score:
            best_score = score
            best_span = span
    return best_span, best_score


def locate_answer_block(
    block_text: str,
    word_boxes: List[Dict[str, Any]],
    img_width: int,
    img_height: int,
    visible_number: Optional[str] = None,
) -> Optional[Dict[str, float]]:
    # 1. Try anchor-based match first (exact label, e.g. "Ans 2")
    span = _find_anchor_span(visible_number, word_boxes)

    # 2. Fall back to fuzzy content matching only if no anchor found
    if not span:
        span, score = _best_window_match(block_text, word_boxes)
        if not span or score < MATCH_THRESHOLD:
            return None

    xs = [w["left"] for w in span]
    ys = [w["top"] for w in span]
    x2s = [w["left"] + w["width"] for w in span]
    y2s = [w["top"] + w["height"] for w in span]

    x_min, y_min = min(xs), min(ys)
    x_max, y_max = max(x2s), max(y2s)

    pad_x, pad_y = 6, 6
    x_min = max(0, x_min - pad_x)
    y_min = max(0, y_min - pad_y)
    x_max = min(img_width, x_max + pad_x)
    y_max = min(img_height, y_max + pad_y)

    return {
        "x_pct": round(x_min / img_width * 100, 2),
        "y_pct": round(y_min / img_height * 100, 2),
        "width_pct": round((x_max - x_min) / img_width * 100, 2),
        "height_pct": round((y_max - y_min) / img_height * 100, 2),
    }
import hashlib
import math
import re
from typing import List


def embed_text(text: str, dimension: int) -> List[float]:
    if dimension <= 0:
        raise ValueError("dimension must be positive.")

    tokens = re.findall(r"\w+", text.lower())
    vector = [0.0] * dimension
    for token in tokens:
        digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
        index = int(digest, 16) % dimension
        vector[index] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return vector
    return [value / norm for value in vector]

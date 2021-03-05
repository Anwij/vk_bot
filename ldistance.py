def is_appropriate_word(word: str, correct_word: str) -> bool:
    l = len(word)
    cl = len(correct_word)

    if abs(l - cl) >= 2:
        return False

    d_matrix = [[0] * (cl + 1) for _ in range(l + 1)]

    for i in range(l + 1):
        d_matrix[i][0] = i
    for i in range(cl + 1):
        d_matrix[0][i] = i

    for i in range(1, l + 1):
        for j in range(1, cl + 1):
            addition = int(word[i - 1] != correct_word[j - 1])
            d_matrix[i][j] = min(
                d_matrix[i - 1][j] + 1,
                d_matrix[i][j - 1] + 1,
                d_matrix[i - 1][j - 1] + addition
            )

    return d_matrix[l][cl] <= 1

# shannon.py

from collections import Counter


def assign_codes(symbols: dict[str, int], code: str) -> dict[str, int]:
    # return symbol with corresponding code
    if len(symbols) == 1:
        return {k: code for k in symbols}

    # divide symbols
    total_freq = sum(symbols.values())
    half_freq = 0
    for i, (symbol, freq) in enumerate(symbols.items()):
        half_freq += freq

        if half_freq >= total_freq / 2:
            left_symbols = {k: v for j, (k, v) in enumerate(symbols.items()) if j <= i}
            right_symbols = {k: v for j, (k, v) in enumerate(symbols.items()) if j > i}
            break

    # append codes
    left_code = assign_codes(left_symbols, f'{code}0')
    right_code = assign_codes(right_symbols, f'{code}1')

    return {**left_code, **right_code}


def shannon_fano(data: str) -> dict[str, int]:
    if not data:
        return {}

    freq = dict(Counter(data).most_common())
    print(f'frequencies: {freq}')
    return assign_codes(freq, '')


def main():
    data = 'HOCHSCHULE'
    codes = shannon_fano(data)
    print(f'codes: {codes}')
    return


if __name__ == '__main__':
    main()

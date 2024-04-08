# shannon.py

def shannon(data):
    total_occurence = 0
    for elem in data:
        total_occurence += elem[0]

    count = 0
    for i, elem in enumerate(data):
        count += elem[0]
        if count == total_occurence // 2:
            count += elem[0]
            break
        if count >= total_occurence // 2:
            print(f'elem: {elem}, idx: {i}, count: {count}')
            break

    return


def main():
    word = "HOCHSCHULE"
    data = list(set([(word.count(letter), letter, "") for letter in word]))
    sorted_data = sorted(data, key=lambda x: x[0], reverse=True)
    print(f'sorted data: {sorted_data}')
    result = shannon(data)


if __name__ == '__main__':
    main()

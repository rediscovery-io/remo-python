from remo import datasets

if __name__ == '__main__':

    data = datasets.list(limit=3)
    for d in data:
        print('Dataset:', d.name)
        print('Files:')
        for img in d:
            print(img.name, img.img.size)
        print()

    print('Batch:')
    for b in data[0].batch_iter(3):
        for img in b:
            print(img.name, img.img.size)
        print()
    print()

    print('Sample:')
    for img in data[0].sample(3):
        print(img.name, img.img.size)

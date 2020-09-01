path_to_images = "./small_flowers/images"
mapping_json_path = os.path.join("small_flowers/annotations", "mapping.json")

cat_to_index = { 0 : 'Pink Primrose',  
                 1 : 'Hard-leaved Pocket Orchid', 
                 2 : 'Canterbury Bells'}

mapping = { value : key for (key, value) in cat_to_index.items()}

classes_dir = ["1", "2", "3"]

root_dir = "./small_flowers/images"
train_ratio = 0.8
val_ratio = train_ratio 
test_ratio = val_ratio + 0.1

for label in classes_dir:
    if not os.path.exists(os.path.join(root_dir,  'dataset/train', label)):
        os.makedirs(os.path.join(root_dir, 'dataset/train', label))
        os.makedirs(os.path.join(root_dir, 'dataset/val', label))
        os.makedirs(os.path.join(root_dir, 'dataset/test', label))

        label_folder = os.path.join(root_dir,  label)

        ims = os.listdir(label_folder)
        np.random.shuffle(ims)

        train, val, test = np.split(np.array(ims),
                                [int(len(ims)*(val_ratio)),
                                    int(len(ims)*(test_ratio))])
        train = [os.path.join(label_folder, name) for name in train.tolist()]
        val = [os.path.join(label_folder, name) for name in val.tolist()]
        test = [os.path.join(label_folder, name) for name in test.tolist()]

        for name in train:
            shutil.copy(name, os.path.join(root_dir, 'dataset/train', label))

        for name in val:
            shutil.copy(name, os.path.join(root_dir, 'dataset/val', label))

        for name in test:
            shutil.copy(name, os.path.join(root_dir, 'dataset/test', label))


images_dir = "./small_flowers/images/dataset"

train_dataset = datasets.ImageFolder(os.path.join(images_dir, "train"), transform = train_transforms)
test_dataset = datasets.ImageFolder(os.path.join(images_dir, "test"), transform = test_valid_transforms)
valid_dataset = datasets.ImageFolder(os.path.join(images_dir, "val"), transform = test_valid_transforms)

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=2)
val_loader = torch.utils.data.DataLoader(valid_dataset, batch_size=2,  shuffle=False, num_workers=2)
test_loader = torch.utils.data.DataLoader(test_dataset,batch_size=1, shuffle=False, num_workers=2)

dataloaders = { "train" : train_loader, "valid" : val_loader, "test" : test_loader}


def imshow(inp, title=None):
    """Imshow for Tensor."""

    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = std * inp + mean
    inp = np.clip(inp, 0, 1)
    plt.imshow(inp)
    if title is not None:
        plt.title(title)
    plt.pause(0.001)  # pause a bit so that plots are updated

inputs, classes = next(iter(dataloaders['train']))
class_names = train_dataset.classes
# Make a grid from batch
out = torchvision.utils.make_grid(inputs)
imshow(out, title=[cat_to_index[class_names[x]] for x in classes])

inputs, classes = next(iter(dataloaders['valid']))
# Make a grid from batch
out = torchvision.utils.make_grid(inputs)
imshow(out, title=[cat_to_index[class_names[x]] for x in classes])


def visualize_model(model):
    images_so_far = 0
    fig = plt.figure()

    for inputs, labels in tqdm.tqdm(dataloaders['test']):
        outputs = model(inputs)
        _, preds = torch.max(outputs.data, 1)
        for j in range(inputs.size()[0]):
            images_so_far += 1
            #ax = plt.subplot(num_images, 2, images_so_far)
            ax.axis('off')
            ax.set_title('predicted: {}'.format(class_names[preds[j]]))
            imshow(inputs.data[j], title='predicted: {} \n original: {}'.format(cat_to_index[class_names[preds[j]]], cat_to_index[class_names[labels[0].item()]]))

visualize_model(test_model)


import glob
import os
from shutil import copyfile
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import copy

def arrange_folders(classes, root):
    """
    Given dataframe and directory path containing the images of the classes
    Arranges samples as given below:
        root/phase/class/xxx.ext
    Args:
        root: string. Root directory path.
        phase: string. 'train' or 'val'
        cls: string.
    """
    for phase in ['train','val']:
        df = pd.read_csv(phase + '_cats_dogs.csv')
        for cls in classes:
            images = df.loc[df['class'] == cls].file_name.values
            phase_path = os.path.join(root, phase)
            if not os.path.exists(phase_path):
                os.mkdir(phase_path)
            class_path = os.path.join(phase_path, cls)
            if not os.path.exists(class_path):
                os.mkdir(class_path)
            for im in images:
                copyfile(os.path.join(root + cls, im), os.path.join(class_path, im))

def prepare_datasets(root_path, phase):
    dataset = datasets.ImageFolder(os.path.join(root_path, phase),
                                         transforms.Compose(
                                             [transforms.RandomResizedCrop(224),
                                              transforms.RandomHorizontalFlip(),
                                              transforms.ToTensor(),
                                              transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])]))
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=4, shuffle=True, num_workers=4)
    
    return dataset, dataloader

def train_model(train_dataset, val_dataset, train_dataloader, val_dataloader, model_path):
    datasizes = {x: len(val_dataset) if x == 'val' else len(train_dataset) for x in ['train', 'val']}
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # load pre-trained resnet18
    model_ft = models.resnet18(pretrained=True)
    num_ftrs = model_ft.fc.in_features
    num_classes = len(train_dataset.classes)

    # reset the final fully connected layer
    model_ft.fc = nn.Linear(num_ftrs, num_classes)

    model_ft = model_ft.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model_ft.parameters(), lr=0.001, momentum=0.9)

    best_model_weights = copy.deepcopy(model_ft.state_dict())
    best_acc = 0.0
    epochs = 3
    for epoch in range(epochs):
        for phase in ['train', 'val']:

            running_loss = 0.0
            running_corrects = 0

            if phase == 'train':
                model_ft.train()
                dataloader = train_dataloader
            else:
                model_ft.eval()
                dataloader = val_dataloader

            for images, labels in dataloader:
                images = images.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                outputs = model_ft(images)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_corrects += torch.sum(preds == labels.data)
            else:
                epoch_acc = running_corrects.double() / datasizes[phase]

            if phase == 'val':
                if epoch_acc > best_acc:
                    best_acc = epoch_acc
                    best_model_weights = copy.deepcopy(model_ft.state_dict())

    print(f'Best Val Acc: {best_acc}')
    torch.save(model_ft.state_dict(), model_path)
    return model_ft


def predict(train_dataset, val_dataloader, model, model_path):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(model_path))
    class_names = train_dataset.classes
    df_preds = pd.DataFrame(columns=['file_name', 'class'])

    with torch.no_grad():
        for i, (inputs, _) in enumerate(val_dataloader, 0):
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            sample_fname, _ = val_dataloader.dataset.samples[i]
            sample_basename = sample_fname.split('/')[-1]
            for k in range(inputs.shape[0]):
                df_preds.loc[len(df_preds) + 1] = [sample_basename, class_names[preds[k]]]
    return df_preds
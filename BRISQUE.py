
from scipy.signal import convolve2d
from torchvision.transforms.functional import to_tensor
import torch
from torch import nn
import torch.nn.functional as F
from PIL import Image
import numpy as np


class CNNIQAnet(nn.Module):
    def __init__(self, ker_size=7, n_kers=50, n1_nodes=800, n2_nodes=800):
        super(CNNIQAnet, self).__init__()
        self.conv1  = nn.Conv2d(1, n_kers, ker_size)
        self.fc1    = nn.Linear(2 * n_kers, n1_nodes)
        self.fc2    = nn.Linear(n1_nodes, n2_nodes)
        self.fc3    = nn.Linear(n2_nodes, 1)
        self.dropout = nn.Dropout()

    def forward(self, x):
        x  = x.view(-1, x.size(-3), x.size(-2), x.size(-1))  #

        h  = self.conv1(x)

        # h1 = F.adaptive_max_pool2d(h, 1)
        # h2 = -F.adaptive_max_pool2d(-h, 1)
        h1 = F.max_pool2d(h, (h.size(-2), h.size(-1)))
        h2 = -F.max_pool2d(-h, (h.size(-2), h.size(-1)))
        h  = torch.cat((h1, h2), 1)  # max-min pooling
        h  = h.squeeze(3).squeeze(2)

        h  = F.relu(self.fc1(h))
        h  = self.dropout(h)
        h  = F.relu(self.fc2(h))

        q  = self.fc3(h)
        return q

class BRISQUE:
    def __init__(self):
        self.model = CNNIQAnet(ker_size=7,n_kers=50,n1_nodes=800,n2_nodes=800)
        model_file='models/CNNIQA-LIVE'
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.load_state_dict(torch.load(model_file,map_location=device))
        self.model.eval()


    def localNormalization(self,patch, P=3, Q=3, C=1):
        kernel = np.ones((P, Q)) / (P * Q)
        patch_mean = convolve2d(patch, kernel, boundary='symm', mode='same')
        patch_sm = convolve2d(np.square(patch), kernel, boundary='symm', mode='same')
        patch_std = np.sqrt(np.maximum(patch_sm - np.square(patch_mean), 0)) + C
        patch_ln = torch.from_numpy((patch - patch_mean) / patch_std).float().unsqueeze(0)
        return patch_ln

    def nonOverlappingCropPatches(self,im, patch_size=32, stride=32):
        w, h = im.size
        patches = ()
        for i in range(0, h - stride, stride):
            for j in range(0, w - stride, stride):
                patch = to_tensor(im.crop((j, i, j + patch_size, i + patch_size)))
                patch = self.localNormalization(patch[0].numpy())
                patches = patches + (patch,)
        return patches

    def getScore(self,img):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        img = Image.fromarray(np.uint8(img)).convert('L')
        patches = self.nonOverlappingCropPatches(img, 32, 32)
        score=-1
        with torch.no_grad():
            patch_scores = self.model(torch.stack(patches).to(device))
            score=patch_scores.mean().item()
        return score
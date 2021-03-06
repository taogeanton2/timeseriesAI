# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/101_ResNet.ipynb (unless otherwise specified).

__all__ = ['ResBlock', 'ResNet']

# Cell
from ..imports import *
from .layers import *

# Cell
class ResBlock(nn.Module):
    def __init__(self, ni, nf, ks=[7, 5, 3]):
        super().__init__()
        self.conv1 = convlayer(ni, nf, ks[0])
        self.conv2 = convlayer(nf, nf, ks[1])
        self.conv3 = convlayer(nf, nf, ks[2])

        # expand channels for the sum if necessary
        self.shortcut = noop if ni == nf else convlayer(ni, nf, ks=1, act_fn=False)
        self.act_fn = nn.ReLU()

    def forward(self, x):
        res = x
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        sc = self.shortcut(res)
        x += sc
        x = self.act_fn(x)
        return x

class ResNet(nn.Module):
    def __init__(self,c_in, c_out):
        super().__init__()
        nf = 64
        self.block1 = ResBlock(c_in, nf, ks=[7, 5, 3])
        self.block2 = ResBlock(nf, nf * 2, ks=[7, 5, 3])
        self.block3 = ResBlock(nf * 2, nf * 2, ks=[7, 5, 3])
        self.gap = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(nf * 2, c_out)

    def forward(self, x):
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.gap(x).squeeze(-1)
        return self.fc(x)
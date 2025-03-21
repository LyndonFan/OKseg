from torch import nn
from torch.nn import Upsample

class HourGlass(nn.Module):
    """不改变特征图的高宽"""
    def __init__(self,n=4,f=128):
        """
        :param n: hourglass模块的层级数目
        :param f: hourglass模块中的特征图数量
        :return:
        """
        super(HourGlass,self).__init__()
        self._n = n
        self._f = f
        self._init_layers(self._n,self._f)

    def _init_layers(self,n,f):
        # 上分支
        setattr(self,'res'+str(n)+'_1',Residual(f,f))
        # 下分支
        setattr(self,'pool'+str(n)+'_1',nn.MaxPool2d(2,2))
        setattr(self,'res'+str(n)+'_2',Residual(f,f))
        if n > 1:
            self._init_layers(n-1,f)
        else:
            self.res_center = Residual(f,f)
        setattr(self,'res'+str(n)+'_3',Residual(f,f))
        setattr(self,'unsample'+str(n),Upsample(scale_factor=2))


    def _forward(self,x,n,f):
        # 上分支
        up1 = x
        up1 = eval('self.res'+str(n)+'_1')(up1)
        # 下分支
        low1 = eval('self.pool'+str(n)+'_1')(x)
        low1 = eval('self.res'+str(n)+'_2')(low1)
        if n > 1:
            low2 = self._forward(low1,n-1,f)
        else:
            low2 = self.res_center(low1)
        low3 = low2
        low3 = eval('self.'+'res'+str(n)+'_3')(low3)
        up2 = eval('self.'+'unsample'+str(n)).forward(low3)

        return up1+up2

    def forward(self,x):
        return self._forward(x,self._n,self._f)

class Residual(nn.Module):
    """
    残差模块，并不改变特征图的宽高
    """
    def __init__(self,ins,outs):
        super(Residual,self).__init__()
        # 卷积模块
        self.convBlock = nn.Sequential(
            nn.BatchNorm2d(ins),
            nn.ReLU(inplace=True),
            nn.Conv2d(ins,int(outs/2),1),
            nn.BatchNorm2d(int(outs/2)),
            nn.ReLU(inplace=True),
            nn.Conv2d(int(outs/2),int(outs/2),3,1,1),
            nn.BatchNorm2d(int(outs/2)),
            nn.ReLU(inplace=True),
            nn.Conv2d(int(outs/2),outs,1)
        )
        # 跳层
        if ins != outs:
            self.skipConv = nn.Conv2d(ins,outs,1)
        self.ins = ins
        self.outs = outs
    def forward(self,x):
        residual = x
        x = self.convBlock(x)
        if self.ins != self.outs:
            residual = self.skipConv(residual)
        x += residual
        return x

class Lin(nn.Module):
    def __init__(self,numIn=128,numout=4):
        super(Lin,self).__init__()
        self.conv = nn.Conv2d(numIn,numout,1)
        self.bn = nn.BatchNorm2d(numout)
        self.relu = nn.ReLU(inplace=True)
    def forward(self,x):
        return self.relu(self.bn(self.conv(x)))


class KFSGNet(nn.Module):

    def __init__(self):
        super(KFSGNet,self).__init__()
        self.__conv1 = nn.Conv2d(3,64,1)
        self.__relu1 = nn.ReLU(inplace=True)
        self.__conv2 = nn.Conv2d(64,128,1)
        self.__relu2 = nn.ReLU(inplace=True)
        self.__hg = HourGlass()
        self.__lin = Lin(numIn=128, numout=1)# 这里numout等于输出通道数，因此预测点数有几个就输几个
    def forward(self,x):
        x = self.__relu1(self.__conv1(x))
        x = self.__relu2(self.__conv2(x))
        x = self.__hg(x)
        x = self.__lin(x)
        return x


from torch.utils.data import Dataset,DataLoader
import numpy as np
import torch.optim as optim

if __name__ == '__main__':
    from torchsummary import summary
    net = KFSGNet()
    print("Model Architecture:")
    summary(net, (3, 512, 512), device="cpu")
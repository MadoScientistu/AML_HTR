from torchvision import transforms
from cv2 import cvtColor, COLOR_BGR2GRAY, resize, imshow, waitKey
from torch import Tensor as TorchTensor
import PIL


class GrayScale(object):
    def __init__(self):
        pass

    def __call__(self, sample):
        image, transcript = sample["image"], sample["transcript"]
        gray = cvtColor(image, COLOR_BGR2GRAY)
        return {"image": gray, "transcript": transcript}


class Rescale(object):
    def __init__(self, new_height, new_width, max_word_length):
        self.__new_height = new_height
        self.__new_width = new_width
        self.__max_word_length = max_word_length

    def __call__(self, sample):
        image, transcript = sample["image"], sample["transcript"]
        scaled_image = resize(image, (self.__new_width, self.__new_height))
        scaled_transcript = (transcript + self.__max_word_length*" ")[:self.__max_word_length]
        return {"image": scaled_image, "transcript": scaled_transcript}


class ToTensor(object):
    def __init__(self, char_to_int):
        self.__converter = transforms.ToTensor()
        self.__char_to_int = char_to_int

    def __call__(self, sample):
        image, transcript = sample["image"], sample["transcript"]
        tensor = self.__converter(image)
        word = [self.__char_to_int[letter] for letter in transcript]

        return tensor, TorchTensor(word)

class TensorToPIL(object):
    def __init__(self):
        self.__transform = torchvision.transforms.ToPILImage("L")
        self.unsqueezed = False

    def __call__(self, sample):
        if !(type(sample) == torch.Tensor):
            raise ValueError("Can only transform torch.Tensor to PIL Image, not  '{}'".format(type(sample)))
        if sample.ndim == 2:
            sample = sample.unsqueeze(0)
            self.unsqueezed = True
        return self.__transform(sample)

class RandomErasing(object):
    def __init__(self, p=0.1, scale=(0.02, 0.04), ratio=(0.3, 3.3), value=1):
        self.__transform = torchvision.transforms.RandomErasing(p=p, scale=scale, ratio=ratio, value=value)

    def __call__ (self, sample):
        if !(type(sample) == torch.Tensor):
            raise ValueError("Can only perform random erasing torch.Tensor, not  '{}'".format(type(sample)))
        return self.__transform(sample)

class RandomRotateAndTranslate(object):
    def __init__(self, p=0.1, degrees=0, translate=(0.03, 0.03), fillcolor=255):
        self.__transform = torchvision.transforms.RandomApply([torchvision.transforms.RandomAffine(degrees=degrees, translate=translate, fillcolor=fillcolor)], p=p)

    def __call__(self, sample):
        if !(type(sample) == PIL.Image.Image):
            raise ValueError("Can only perform Rotation and Translation on PIL.Image.Image, not  '{}'".format(type(sample)))
        return self.__transform(sample)

class RandomJitter(object):
    def __init__(self, p=0.1):
        self.__transform = torchvision.transforms.RandomApply([torchvision.transforms.ColorJitter()], p=p)

    def __call__(self, sample)
        if !(type(sample) == PIL.Image.Image):
            raise ValueError("Can only perform Jitter on PIL.Image.Image, not  '{}'".format(type(sample)))
        return self.__transform(sample)

class RandomPerspective(object):
    def __init__(self, p=0.1, warp_ratio=0.0003, fillcolor=255):
        self.__transform = torchvision.transforms.Lambda(self.warp)
        self.p = p
        self.warp_ratio = warp_ratio
        self.fillcolor = fillcolor

    def __call__(self, sample):
        if !(type(sample) == PIL.Image.Image):
            raise ValueError("Can only perform random perspective on PIL.Image.Image, not  '{}'".format(type(sample)))
        return self.__transform(sample)

    def warp(self, img):
        if numpy.random.rand() > self.p:
            return img
        pa = torch.Tensor([[0,0], [0,1], [1,0], [1,1]])
        pb = pa + torch.randn(4,2)*self.warp_ratio

        img = img.transform(img.size, PIL.Image.PERSPECTIVE, self.find_coeffs(pa,pb), PIL.Image.BICUBIC, fillcolor=self.fillcolor)
        return img

    def find_coeffs(self, pa, pb):
        matrix = []
        for p1, p2 in zip(pa, pb):
            matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
            matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

        A = numpy.matrix(matrix, dtype=numpy.float)
        B = numpy.array(pb).reshape(8)

        res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
        return numpy.array(res).reshape(8)


def rstrip(lst, value):
    for idx, x in enumerate(reversed(lst)):
        if x != value:
            if idx:
                del lst[-idx:]
            return lst
    return lst


def word_tensor_to_list(tensor):
    return [rstrip(word, 0) for word in tensor.cpu().tolist()]

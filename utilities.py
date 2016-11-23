def InverseRasterScan(a, b, c, d, e):
    if e == 0:
        return (a % ( d // b ) ) * b
    elif e == 1:
        return (a // ( d // b ) ) * c
    else:
        assert False

def Clip3(x, y, z):
    if z < x:
        return x
    elif z > y:
        return y
    else:
        return z
        
def Clip1_Y(x, BitDepth_Y):
    return Clip3(0, (1 << BitDepth_Y) - 1, x)

def Clip1_C(x, BitDepth_C):
    return Clip3(0, (1 << BitDepth_C) - 1, x)

# 6.4.1 Inverse macroblock scanning process
def get_cord_of_mb(mbAddr, MbaffFrameFlag, PicWidthInSamples_L):
    if MbaffFrameFlag == 0:
        x = InverseRasterScan( mbAddr, 16, 16, PicWidthInSamples_L , 0 )
        y = InverseRasterScan( mbAddr, 16, 16, PicWidthInSamples_L , 1 )
        return (x, y)
    else:
        raise NameError("MbaffFrameFlag == 1")

# 6.4.3 Inverse 4x4 luma block scanning process
def get_cord_of_luma4x4(luma4x4BlkIdx):
    x = InverseRasterScan( luma4x4BlkIdx // 4, 8, 8, 16, 0 ) + InverseRasterScan( luma4x4BlkIdx % 4, 4, 4, 8, 0 )
    y = InverseRasterScan( luma4x4BlkIdx // 4, 8, 8, 16, 1 ) + InverseRasterScan( luma4x4BlkIdx % 4, 4, 4, 8, 1 )
    return (x, y)

# 6.4.7 Inverse 4x4 chroma block scanning process
def get_cord_of_chroma4x4(idx):
    x = InverseRasterScan(idx, 4, 4, 8, 0)
    y = InverseRasterScan(idx, 4, 4, 8, 1)
    return (x, y)

def all_satisfy(arr, fn):
    for x in arr:
        if not fn(x):
            return False
    return True
def any_satisfy(arr, fn):
    for x in arr:
        if fn(x):
            return True
    return False

def array_2d(w, h, v = None):
    return [[v for x in range(w)] for y in range(h)]

def pic_paint(img, fname):
    with open(fname, 'w') as outfile:
        w = len(img)
        h = len(img[0])
        for x in range(h):
            for y in range(w):
                print('{0:3d} '.format(img[y][x]), end='', file=outfile)
            print('', file=outfile)

def mat_mult(a, b):
    n = len(a)
    ma = len(a[0])
    p = len(b[0])
    mb = len(b)
    assert ma == mb
    prod = array_2d(n, p)
    for i in range(n):
        for j in range(p):
            prod[i][j] = sum([a[i][k] * b[k][j] for k in range(ma)])
    return prod
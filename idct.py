from utilities import *
import intra_pred

# 8.5 Construct One MB sample array, S'L S'Cb S'Cr
def construct_picture(blk):
    if blk.color == "Y" and blk.size == "4x4":
        dec_luma4x4(blk)
    else:
        assert False

# 8.5.1 transform decoding process for 4x4 luma residual blocks
def dec_luma4x4(blk):
    luma4x4BlkIdx = blk.idx
    coeffLevel = blk.coeffLevel
    # print("CoeffLevel:", coeffLevel)
    c = inv_scan_for_4x4_coeff_slist(coeffLevel)
    # print("Array C:", c)
    r = idct_and_scaling_for_4x4(c, blk)
    # print("Array R:", r)
    if blk.mb.TransformBypassModeFlag == 1:
        raise NameError("8.5.1-3 TransformBypassModeFlag not impl")
    (xO, yO) = get_cord_of_luma4x4(luma4x4BlkIdx)
    u = array_2d(4,4)
    for i in range(4):
        for j in range(4):
            u[i][j] = Clip1_Y(blk.mb.pred_L[xO+j][yO+i]+r[i][j], blk.mb.slice.sps.BitDepth_Y)
    # print("Array U:", u)
    pic_construct(u, blk)

# 8.5.2 transform decoding process for luma samples of Intra_16x16 macroblock prediction mode
def idct_for_luma16x16(mb):
    # 16x16 DC
    c = inv_scan_for_4x4_coeff_slist(mb.luma_i16x16_dc_block.coeffLevel)
    dcY = idct_for_dc_luma_16x16(mb.slice.sps.BitDepth_Y, mb.QP_prime_Y, c, mb)
    # print("DCY:", dcY)
    # rMB
    rMb = array_2d(16,16)
    for blk in mb.luma_blocks:
        lumaList = [None] * 16
        (i,j) = [(0,0),(0,1),(1,0),(1,1),
                 (0,2),(0,3),(1,2),(1,3),
                 (2,0),(2,1),(3,0),(3,1),
                 (2,2),(2,3),(3,2),(3,3)][blk.idx]
        lumaList[0] = dcY[i][j]
        for k in range(1,16):
            lumaList[k] = blk.coeffLevel[k-1]
        c = inv_scan_for_4x4_coeff_slist(lumaList)
        r = idct_and_scaling_for_4x4(c, blk)
        (xO, yO) = get_cord_of_luma4x4(blk.idx)
        for i in range(4):
            for j in range(4):
                rMb[xO+j][yO+i] = r[i][j]
    if mb.TransformBypassModeFlag == 1 and mb.Intra16x16PredMode in [0,1]:
        raise NameError("TransformBypassModeFlag not impl")
    # print("rMB:", rMb)
    u = array_2d(16,16)
    for i in range(16):
        for j in range(16):
            u[i][j] = Clip1_Y(mb.pred_L[j][i] + rMb[j][i], mb.slice.sps.BitDepth_Y)
    pic_construct_16x16(u, mb)

# 8.5.3 transform decoding process for 8x8 luma residual blocks
def idct_for_luma8x8():
    assert False

# 8.5.4 transform decoding process for chroma samples
# def idct_for_chroma(mb):
#     for iCbCr in [1,2]:
#         idct_for_chroma_C(mb, iCbCr)

def idct_for_chroma_C(mb, iCbCr):
    print(mb.idx, iCbCr, "idcting")
    if mb.slice.sps.ChromaArrayType == 3:
        raise NameError("8.5.5 not impl")
    else:
        numChroma4x4Blks =(mb.slice.sps.MbWidthC // 4) * (mb.slice.sps.MbHeightC // 4)
        #1-a
        if mb.slice.sps.ChromaArrayType == 1:
            cDC = mb.chroma_dc_blocks[iCbCr-1].coeffLevel
            c = [[cDC[0],cDC[1]],
                 [cDC[2],cDC[3]]]
        else:
            raise NameError("Chroma Array Type == 2")
        #1-b
        dcC = idct_and_scaling_for_dc_chroma(c, mb, iCbCr)
        # print("dcC:", dcC)
        rMb = array_2d(mb.slice.sps.MbWidthC, mb.slice.sps.MbHeightC)
        for blkIdx in range(numChroma4x4Blks):
            chromaList = [None] * 16
            #2-a
            (i, j) = [(0,0),(0,1),(1,0),(1,1)][blkIdx]
            chromaList[0] = dcC[i][j]
            for k in range(1,16):
                chromaList[k] = mb.chroma_ac_blocks[iCbCr-1][blkIdx].coeffLevel[k-1]
            #2-b
            c = inv_scan_for_4x4_coeff_slist(chromaList)
            # print("c:", c)
            #2-c
            r = idct_and_scaling_for_4x4(c, mb.chroma_ac_blocks[iCbCr-1][blkIdx])
            # print("r:", r)
            #2-d
            (xO, yO) = get_cord_of_chroma4x4(blkIdx)
            #2-e
            for i in range(4):
                for j in range(4):
                    rMb[xO+j][yO+i] = r[i][j]
            # print(xO+j, yO+i, "-> rMB:",rMb)
        #3
        if mb.TransformBypassModeFlag == 1:
            raise NameError("Bypass not impl")
        #4
        u =  array_2d(mb.slice.sps.MbWidthC, mb.slice.sps.MbHeightC)
        for i in range(mb.slice.sps.MbWidthC):
            for j in range(mb.slice.sps.MbHeightC):
                pred_C = mb.pred_Cb if iCbCr == 1 else mb.pred_Cr
                # print(pred_C)
                u[i][j] = Clip1_C(pred_C[j][i] + rMb[j][i], mb.slice.sps.BitDepth_C)
        #5
        pic_construct_chroma(u, mb, iCbCr)

# 8.5.5 transform decoding process for chroma samples with ChromaArrayType equal to 3

# 8.5.6 Inverse scanning process for 4x4 transform coefficients and scaling lists
def inv_scan_for_4x4_coeff_slist(arr):
    zigzag = [(0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (0, 3), (1, 2), (2, 1), (3, 0), (3, 1), (2, 2), (1, 3), (2, 3), (3, 2), (3, 3)]
    c = array_2d(4,4)
    # for (idx, v) in enumerate(arr):
    #     (x, y) = zigzag[idx]
    #     c[x][y] = v
    #     print(idx, v, "->", x,y,"res",c)
    for i in range(16):
        (x,y) = zigzag[i]
        c[x][y] = arr[i]
    return c

# 8.5.7 Inverse scanning process for 8x8 transform coefficients and scaling lists
def inv_scan_for_8x8():
    assert False

# 8.5.8 Derivation process for chroma quantisation parameters
def get_chroma_qp():
    assert False

# 8.5.9 Derivation process for scaling functions
def get_4x4_scaling_fn(blk):
    mbIsInterFlag = 1 if "Inter" in blk.mb.pred_mode else 0
    iYCbCr = blk.mb.slice.colour_plane_id if blk.mb.slice.sps.separate_colour_plane_flag == 1 else ["Y", "Cb", "Cr"].index(blk.color)
    weightScale4x4 = inv_scan_for_4x4_coeff_slist(blk.mb.slice.pps.ScalingList4x4[iYCbCr + (3 if mbIsInterFlag == 1 else 0)])
    LevelScale4x4 = [array_2d(4,4)]*6
    for m in range(6):
        for i in range(4):
            for j in range(4):
                LevelScale4x4[m][i][j] = weightScale4x4[i][j] * normAdjust4x4(m, i, j)
    # LevelScale8x8 not impl
    return LevelScale4x4
def normAdjust4x4(m, i, j):
    v = [[10,16,13],
         [11,18,14],
         [13,20,16],
         [14,23,18],
         [16,25,20],
         [18,29,23]]
    if (i%2, j%2) == (0, 0):
        return v[m][0]
    elif (i%2, j%2) == (1, 1):
        return v[m][1]
    else:
        return v[m][2]

# 8.5.10 Scaling and transformation process for DC transform coefficients for Intra_16x16 macroblock type
def idct_for_dc_luma_16x16(bitDepth, qP, c, mb):
    LevelScale4x4 = get_4x4_scaling_fn(mb.luma_i16x16_dc_block)
    dcY = array_2d(4, 4)
    if mb.TransformBypassModeFlag == 1:
        raise NameError("TransBypass not impl")
    else:
        a = [[ 1, 1, 1, 1],
             [ 1, 1,-1,-1],
             [ 1,-1,-1, 1],
             [ 1,-1, 1,-1]]
        f = mat_mult(a, c)
        f = mat_mult(f, a)
        if qP >= 36:
            for i in range(4):
                for j in range(4):
                    dcY[i][j] = (f[i][j] * LevelScale4x4[qP % 6][0][0]) << (qP // 6 - 6)
        else:
            for i in range(4):
                for j in range(4):
                    dcY[i][j] = (f[i][j] * LevelScale4x4[qP % 6][0][0]) + (1 << (5 - qP // 6)) >> (6 - qP // 6)
    return dcY

# 8.5.11 Scaling and transformation process for chroma DC transform coefficients
def idct_and_scaling_for_dc_chroma(c, mb, iCbCr):
    bitDepth = mb.slice.sps.BitDepth_C
    qP = mb.QP_prime_C
    if mb.TransformBypassModeFlag == 1:
        raise NameError("Bypass")
    else:
        f = idct_for_dc_chroma(bitDepth, c, mb)
        dcC = scaling_for_dc_chroma(bitDepth, qP, f, mb, iCbCr)
    return dcC

# 8.5.11.1 Transformation process for chroma DC transform coefficients
def idct_for_dc_chroma(bitDepth, c, mb):
    f = array_2d(mb.slice.sps.MbWidthC // 4, mb.slice.sps.MbHeightC // 4)
    if mb.slice.sps.ChromaArrayType == 1:
        a = [[1, 1], [1, -1]]
        f = mat_mult(a, c)
        f = mat_mult(f, a)
    else:
        raise NameError("Chroma Array T == 2")
    return f

# 8.5.11.2 Scaling process for chroma DC transform coefficients
def scaling_for_dc_chroma(bitDepth, qP, f, mb, iCbCr):
    LevelScale4x4 = get_4x4_scaling_fn(mb.chroma_dc_blocks[iCbCr-1])
    dcC = array_2d(mb.slice.sps.MbWidthC // 4, mb.slice.sps.MbHeightC // 4)
    if mb.slice.sps.ChromaArrayType == 1:
        for i in range(2):
            for j in range(2):
                dcC[i][j] = ((f[i][j] * LevelScale4x4[qP % 6][0][0]) << (qP // 6)) >> 5
    else:
        raise NameError("Chroma Array T == 2")
    return dcC

# 8.5.12 Scaling and transformation process for residual 4x4 blocks
def idct_and_scaling_for_4x4(c, blk):
    bitDepth = blk.mb.slice.sps.BitDepth_Y if blk.color == "Y" else blk.mb.slice.sps.BitDepth_C
    sMbFlag = 0 # maybe bug
    if blk.color == "Y" and sMbFlag == 0:
        qP = blk.mb.QP_prime_Y
    elif blk.color in ["Cb", "Cr"] and sMbFlag == 0:
        qP = blk.mb.QP_prime_C
    else:
        raise NameError("sMbFlag not impl")
    if blk.mb.TransformBypassModeFlag == 1:
        raise NameError("sMbFlag not impl")
    else:
        d = scaling_for_4x4(bitDepth, qP, c, blk)
        r = idct_for_4x4(bitDepth, d)
    return r

# 8.5.12.1 Scaling process for residual 4x4 blocks
def scaling_for_4x4(bitDepth, qP, c, blk):
    LevelScale4x4 = get_4x4_scaling_fn(blk)
    d = array_2d(4,4)
    if (blk.color == "Y" and "Intra16x16" in blk.mb.pred_mode) or blk.color in ["Cb","Cr"]:
        d[0][0] = c[0][0]
    if qP >= 24:
        for i in range(4):
            for j in range(4):
                d[i][j] = (c[i][j] * LevelScale4x4[qP%6][i][j]) << (qP//6-4)
    else:
        for i in range(4):
            for j in range(4):
                d[i][j] = (c[i][j] * LevelScale4x4[qP%6][i][j] + 2**(3-qP//6)) >> (4 - qP//6)
    if (blk.color == "Y" and "Intra16x16" in blk.mb.pred_mode) or blk.color in ["Cb","Cr"]:
        d[0][0] = c[0][0]
    return d

# 8.5.12.2 Transformation process for residual 4x4 blocks
def idct_for_4x4(bitDepth, d):
    e = array_2d(4,4)
    for i in range(4):
        e[i][0] = d[i][0] + d[i][2]
        e[i][1] = d[i][0] - d[i][2]
        e[i][2] = (d[i][1] >> 1) - d[i][3]
        e[i][3] = d[i][1] + (d[i][3] >> 1)
    f = array_2d(4,4)
    for i in range(4):
        f[i][0] = e[i][0] + e[i][3]
        f[i][1] = e[i][1] + e[i][2]
        f[i][2] = e[i][1] - e[i][2]
        f[i][3] = e[i][0] - e[i][3]
    g = array_2d(4,4)
    for j in range(4):
        g[0][j] = f[0][j] + f[2][j]
        g[1][j] = f[0][j] - f[2][j]
        g[2][j] = (f[1][j] >> 1) - f[3][j]
        g[3][j] = f[1][j] + (f[3][j] >> 1)
    h = array_2d(4,4)
    for j in range(4):
        h[0][j] = g[0][j] + g[3][j]
        h[1][j] = g[1][j] + g[2][j]
        h[2][j] = g[1][j] - g[2][j]
        h[3][j] = g[0][j] - g[3][j]
    r = array_2d(4,4)
    for i in range(4):
        for j in range(4):
            r[i][j] = (h[i][j] + 2**5) >> 6
    return r

# 8.5.13 Scaling and transformation process for residual 8x8 blocks
def idct_and_scaling_for_8x8():
    assert False
# 8.5.13.1 Scaling process for residual 8x8 blocks
def scaling_for_8x8():
    assert False
# 8.5.13.2 Transformation process for residual 8x8 blocks
def idct_for_8x8():
    assert False

# 8.5.14 Picture construction process
def pic_construct(u, blk):
    if blk.color == "Y":
        (xP, yP) = get_cord_of_mb(blk.mb.idx, blk.mb.slice.MbaffFrameFlag, blk.mb.slice.PicWidthInSamples_L)
        if blk.size == "16x16":
            (xO, yO) = (0, 0)
            nE = 16
        elif blk.size == "4x4":
            (xO, yO) = get_cord_of_luma4x4(blk.idx)
            nE = 4
        elif blk.size == "8x8":
            raise NameError("8x8 not impl")
        else:
            raise NameError("not impl")

        if blk.mb.slice.MbaffFrameFlag == 0:
            for i in range(nE):
                for j in range(nE):
                    # print(i,j,xP+xO+j,yP+yO+i, "<-", u[i][j])
                    blk.mb.slice.S_prime_L[xP+xO+j][yP+yO+i] = u[i][j]
        else:
            raise NameError("MbaffFrameFlag == 1")
        # print(blk.mb.slice.S_prime_L)
    else:
        raise NameError("Chroma not impl")

def pic_construct_16x16(u, mb):
    (xP, yP) = get_cord_of_mb(mb.idx, mb.slice.MbaffFrameFlag, mb.slice.PicWidthInSamples_L)
    (xO, yO) = (0, 0)
    nE = 16
    if mb.slice.MbaffFrameFlag == 0:
        for i in range(nE):
            for j in range(nE):
                mb.slice.S_prime_L[xP+xO+j][yP+yO+i] = u[i][j]
    else:
        raise NameError("MbaffFrameFlag == 1")
        # print(blk.mb.slice.S_prime_L)

def pic_construct_chroma(u, mb, iCbCr):
    (xP, yP) = get_cord_of_mb(mb.idx, mb.slice.MbaffFrameFlag, mb.slice.PicWidthInSamples_L)
    assert len(u) == mb.slice.sps.MbWidthC
    nW = mb.slice.sps.MbWidthC
    nH = mb.slice.sps.MbHeightC
    (xO, yO) = (0, 0)
    assert mb.slice.MbaffFrameFlag == 0
    if iCbCr == 1:
        SC = mb.slice.S_prime_Cb
    elif iCbCr == 2:
        SC = mb.slice.S_prime_Cr
    else:
        raise NameError("iCbCr error")
    for i in range(nH):
        for j in range(nW):
            SC[xP // mb.slice.sps.SubWidthC + xO + j][yP // mb.slice.sps.SubHeightC + yO + i] = u[i][j]

# 8.5.15 Intra residual transform-byassert False decoding process
def tran_byp():
    assert False
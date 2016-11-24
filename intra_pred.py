from utilities import *
from pprint import pprint
import idct
# 8.3 Intra prediction process

def luma_pred(mb):
    # print("decoding mb ", mb.idx)
    MvCnt = 0
    if mb.pred_mode == "Intra4x4":
        intra_4x4_luma(mb)
    elif mb.pred_mode == "Intra8x8":
        raise NameError("8x8 not impl")
    elif mb.pred_mode == "Intra16x16":
        intra_16x16_luma(mb)
    # else:
    #     raise NameError("8.3.4")

# 8.3.1 Intra_4x4 prediction process for luma samples
def intra_4x4_luma(mb):
    for blk in mb.luma_blocks:
        gen_intra_4x4_pred_mode(blk)
        gen_pred4x4_L(blk)
        (xO, yO) = get_cord_of_luma4x4(blk.idx)
        # blk.pred_L = array_2d(4,4)
        for x in range(4):
            for y in range(4):
                blk.mb.pred_L[xO+x][yO+y] = blk.pred4x4_L[x][y]
        # print("Pred_L:", blk.mb.pred_L)
        idct.dec_luma4x4(blk)

# 8.3.1.1 Derivation process for Intra4x4PredMode -> blk.Intra4x4PredMode
def gen_intra_4x4_pred_mode(blk):
    luma4x4BlkIdx = blk.idx
    mbs = blk.mb.slice.mbs
    (mbAddrA, blkIdxA) = blk.luma_neighbor("A")
    (mbAddrB, blkIdxB) = blk.luma_neighbor("B")
    # print(mbAddrA, mbAddrB)
    if mbAddrA == None or mbAddrB == None or \
        ("Inter" in mbs[mbAddrA].pred_mode and mbs[mbAddrA].constrained_intra_pred_flag == 1) or \
        ("Inter" in mbs[mbAddrB].pred_mode and mbs[mbAddrB].constrained_intra_pred_flag == 1):
        dcPredModePredictedFlag = 1
    else:
        dcPredModePredictedFlag = 0
    #3 derive MxMPredMode(A|B)
    if dcPredModePredictedFlag == 1 or (not (mbs[mbAddrA].pred_mode in ["Intra4x4", "Intra8x8"])):
        intraMxMPredModeA = 2
    else:
        if mbs[mbAddrA].pred_mode == "Intra4x4":
            intraMxMPredModeA = mbs[mbAddrA].luma_blocks[blkIdxA].Intra4x4PredMode
        else:
            raise NameError("8x8 not impl")
    if dcPredModePredictedFlag == 1 or (not (mbs[mbAddrB].pred_mode in ["Intra4x4", "Intra8x8"])):
        intraMxMPredModeB = 2
    else:
        if mbs[mbAddrB].pred_mode == "Intra4x4":
            intraMxMPredModeB = mbs[mbAddrB].luma_blocks[blkIdxB].Intra4x4PredMode
        else:
            raise NameError("8x8 not impl")
    #4 derive Intra4x4PredMode
    predIntra4x4PredMode = min(intraMxMPredModeA, intraMxMPredModeB)
    if blk.prev_intra4x4_pred_mode_flag:
        blk.Intra4x4PredMode = predIntra4x4PredMode
    else:
        if blk.rem_intra4x4_pred_mode < predIntra4x4PredMode:
            blk.Intra4x4PredMode = blk.rem_intra4x4_pred_mode
        else:
            blk.Intra4x4PredMode = blk.rem_intra4x4_pred_mode + 1
    # print("Intra4x4PredMode:", ["V", "H", "DC", "DDL","DDR", "VR", "HD", "VL", "HU"][blk.Intra4x4PredMode])

# 8.3.1.2 Intra_4x4 sample prediction -> pred4x4_L
def gen_pred4x4_L(blk):
    mbs = blk.mb.slice.mbs
    (xO, yO) = get_cord_of_luma4x4(blk.idx)
    p = array_2d(9,5)
    for y in  range(-1,4):
        xs = range(-1,8) if y == -1 else [-1]
        for x in xs:
            xN = xO + x
            yN = yO + y
            (mbAddrN, xW, yW) = blk.mb.luma_neighbor_location(xN, yN)
            if mbAddrN == None or \
               ("Inter" in mbs[mbAddrN].pred_mode and mbs[mbAddrN].constrained_intra_pred_flag == 1) or \
               (x > 3 and blk.idx in [3,11]):
               # ignore 3-3 macroblock mbAddrN has mb_type equal to SI and constrained_intra_pred_flag is equal to 1 and
               # the current macroblock does not have mb_type equal to SI
                p[x+1][y+1] = None
            else:
                mb = mbs[mbAddrN]
                MbaffFrameFlag = mb.slice.MbaffFrameFlag
                PicWidthInSamples_L = mb.slice.PicWidthInSamples_L
                (xM, yM) = get_cord_of_mb(mbAddrN, MbaffFrameFlag, PicWidthInSamples_L)
                if MbaffFrameFlag == 0:
                    p[x+1][y+1] = blk.mb.slice.S_prime_L[xM+xW][yM+yW]
                else:
                    raise NameError("Field mb may exist")
    if ([p[5][0], p[6][0], p[7][0], p[8][0]] == [None,None,None,None]) and \
       p[4][0] != None:
        for x in range(5,9):
            p[x][0] = p[4][0]
    # print("Array P:", p)

    pred4x4_fns = [pred4x4_V, pred4x4_H, pred4x4_DC, pred4x4_DDL,
                   pred4x4_DDR, pred4x4_VR, pred4x4_HD, pred4x4_VL, pred4x4_HU]
    pred4x4_fn = pred4x4_fns[blk.Intra4x4PredMode]
    blk.pred4x4_L = pred4x4_fn(blk, p)
    # print("Pred4x4_L:", blk.pred4x4_L)

# 8.3.1.2.1 Specification of Intra_4x4_Vertical prediction mode
def pred4x4_V(blk, p):
    pred4x4_L = array_2d(4,4)
    for x in range(4):
        for y in range(4):
            pred4x4_L[x][y] = p[x+1][0]
    return pred4x4_L

# 8.3.1.2.2 Specification of Intra_4x4_Horizontal prediction mode
def pred4x4_H(blk, p):
    pred4x4_L = array_2d(4,4)
    for x in range(4):
        for y in range(4):
            pred4x4_L[x][y] = p[0][y+1]
    return pred4x4_L
# 8.3.1.2.3 Specification of Intra_4x4_DC prediction mode
def pred4x4_DC(blk, p):
    pred4x4_L = array_2d(4,4)
    pX0 = [p[1][0],p[2][0],p[3][0],p[4][0]]
    p0Y = [p[0][1],p[0][2],p[0][3],p[0][4]]
    if all_satisfy(pX0, lambda x: x != None) and \
       all_satisfy(p0Y, lambda x: x != None):
        v = (p[1][0]+p[2][0]+p[3][0]+p[4][0]+p[0][1]+p[0][2]+p[0][3]+p[0][4]+4) >> 3
    elif any_satisfy(pX0, lambda x: x == None) and \
         all_satisfy(p0Y, lambda x: x != None):
        v = (p[0][1]+p[0][2]+p[0][3]+p[0][4]+2) >> 2
    elif any_satisfy(p0Y, lambda x: x == None) and \
         all_satisfy(pX0, lambda x: x != None):
        v = (p[1][0]+p[2][0]+p[3][0]+p[4][0]+2) >> 2
    else:
        v = (1 << (blk.mb.slice.sps.BitDepth_Y - 1))
    for x in range(4):
        for y in range(4):
            pred4x4_L[x][y] = v
    return pred4x4_L

# 8.3.1.2.4 Specification of Intra_4x4_Diagonal_Down_Left prediction mode
def pred4x4_DDL(blk, p):
    pred4x4_L = array_2d(4,4)
    for x in range(4):
        for y in range(4):
            if x == 3 and y == 3:
                pred4x4_L[x][y] = (p[7][0] + 3 * p[8][0] + 2) >> 2
            else:
                pred4x4_L[x][y] = (p[x+y+1][0] + 2*p[x+y+2][0] + p[x+y+3][0] + 2) >> 2
    return pred4x4_L

# 8.3.1.2.5 Specification of Intra_4x4_Diagonal_Down_Right prediction mode
def pred4x4_DDR(blk, p):
    pred4x4_L = array_2d(4,4)
    for x in range(4):
        for y in range(4):
            if x > y:
                pred4x4_L[x][y] = (p[x-y-1][0] + 2*p[x-y][0] + p[x-y+1][0] + 2) >> 2
            elif x < y:
                pred4x4_L[x][y] = (p[0][x-y-1] + 2*p[0][x-y] + p[0][x-y+1] + 2) >> 2
            else:
                pred4x4_L[x][y] = (p[1][0] + 2*p[0][0] + p[0][1] + 2) >> 2
    return pred4x4_L

# 8.3.1.2.6 Specification of Intra_4x4_Vertical_Right prediction mode
def pred4x4_VR(blk, p):
    pred4x4_L = array_2d(4,4)
    for x in range(4):
        for y in range(4):
            zVR = 2 * x - y
            if zVR in [0,2,4,6]:
                pred4x4_L[x][y] = (p[x-(y >> 1)][0] + p[x-(y >> 1)+1][0] + 1) >> 1
            elif zVR in [1,3,5]:
                pred4x4_L[x][y] = (p[x-(y >> 1)-1][0] + 2*p[x-(y >> 1)][0] + p[x-(y >> 1)+1][0] + 2 ) >> 2
            elif zVR == -1:
                pred4x4_L[x][y] = (p[0][1] + 2*p[0][0] + p[1][0] + 2) >> 2
            else:
                pred4x4_L[x][y] = (p[0][y] + 2*p[0][y-1] + p[0][y-2] + 2 ) >> 2
    return pred4x4_L

# 8.3.1.2.7 Specification of Intra_4x4_Horizontal_Down prediction mode
def pred4x4_HD(blk, p):
    pred4x4_L = array_2d(4,4)
    for x in range(4):
        for y in range(4):
            zHD = 2 * y - x
            if zHD in [0,2,4,6]:
                pred4x4_L[x][y]=(p[0][y-(x>>1)] + p[0][y-(x>>1)]+2) >> 1
            elif zHD in [1,3,5]:
                pred4x4_L[x][y]=(p[0][y-(x>.1)-1] + 2*p[0][y-(x>>1)] + p[0][y-(x>>1)+1]+2) >> 2
            elif zHD == -1:
                pred4x4_L[x][y]=(p[0][1]+2*p[0][0]+p[1][0]+2) >> 2
            else:
                pred4x4_L[x][y]=(p[x][0]+2*p[x-1][0]+p[x-2][0]+2) >> 2
    return pred4x4_L

# 8.3.1.2.8 Specification of Intra_4x4_Vertical_Left prediction mode
def pred4x4_VL(blk, p):
    pred4x4_L = array_2d(4,4)
    for x in range(4):
        for y in range(4):
            if y in [0, 2]:
                pred4x4_L[x][y] = (p[x+(y>>1)+1][0] + p[x+(y>>1) + 2][0] + 1) >> 1
            else:
                pred4x4_L[x][y] = (p[x+(y>>1)+1][0] + 2 * p[x+(y>>1)+2][0] + p[x+(y>>1)+3][0] + 2 ) >> 2
    return pred4x4_L

# 8.3.1.2.9 Specification of Intra_4x4_Horizontal_Up prediction mode
def pred4x4_HU(blk, p):
    pred4x4_L = array_2d(4,4)
    for x in range(4):
        for y in range(4):
            zHU = x + 2 * y
            if zHU in [0,2,4]:
                pred4x4_L[x][y] = (p[0][y+(x>>1)+1] + p[0][y+(x >> 1) + 2] + 1 ) >> 1
            elif zHU in [1,3]:
                pred4x4_L[x][y] = (p[0][y+(x>>1)+1] + 2*p[0][y+(x>>1)+2] + p[0][y+(x>>1)+3] + 2) >> 2
            elif zHU == 5:
                pred4x4_L[x][y] = (p[0][3] + 3 * p[0][4] + 2) >> 2
            else:
                pred4x4_L[x][y] = p[0][4]
    return pred4x4_L

# 8.3.3 Intra_16x16 prediction process for luma samples
def intra_16x16_luma(mb):
    cS_L = mb.slice.S_prime_L
    mbs = mb.slice.mbs
    p = array_2d(17,17)
    for x in range(-1,16):
        ys = range(-1,16) if x == -1 else [-1]
        for y in ys:
            (mbAddrN, xW, yW) = mb.luma_neighbor_location(x, y)
            if mbAddrN == None or \
               ("Inter" in mbs[mbAddrN].pred_mode and mbs[mbAddrN].constrained_intra_pred_flag == 1) or \
               (mbs[mbAddrN].mb_type == "SI" and mbs[mbAddrN].constrained_intra_pred_flag == 1):
                p[x+1][y+1] = None
            else:
                MbaffFrameFlag = mb.slice.MbaffFrameFlag
                PicWidthInSamples_L = mb.slice.PicWidthInSamples_L
                (xM, yM) = get_cord_of_mb(mbAddrN, MbaffFrameFlag, PicWidthInSamples_L)
                if MbaffFrameFlag == 0:
                    p[x+1][y+1] = cS_L[xM+xW][yM + yW]
                else:
                    p[x+1][y+1] = cS_L[xM+xW][yM + 2*yW]
                    raise NameError("Field mb may exist")
    pred16x16_fns = [pred16x16_V, pred16x16_H, pred16x16_DC, pred16x16_P]
    pred16x16_fn = pred16x16_fns[mb.Intra16x16PredMode]
    # print("Array P:", p)
    mb.pred_L = pred16x16_fn(p, mb)
    # print("16x16Pred_L:", mb.pred_L)
    idct.idct_for_luma16x16(mb)

# 8.3.3.1 Specification of Intra_16x16_Vertical prediction mode
def pred16x16_V(p, mb):
    pred_L = array_2d(16,16)
    for x in range(16):
        for y in range(16):
            pred_L[x][y] = p[x+1][0]
    return pred_L

# 8.3.3.2 Specification of Intra_16x16_Horizontal prediction mode
def pred16x16_H(p, mb):
    pred_L = array_2d(16,16)
    for x in range(16):
        for y in range(16):
            pred_L[x][y] = p[0][y+1]
    return pred_L

# 8.3.3.3 Specification of Intra_16x16_DC prediction mode
def pred16x16_DC(p, mb):
    pred_L = array_2d(16,16)
    px = [p[x+1][0] for x in range(16)]
    py = [p[0][y+1] for y in range(16)]
    for x in range(16):
        for y in range(16):
            if all_satisfy(px, lambda n: n != None) and all_satisfy(py, lambda n:n != None):
                pred_L[x][y] = (sum(px) + sum(py) + 16) >> 5
            elif any_satisfy(px, lambda n:n == None) and all_satisfy(py, lambda n:n != None):
                pred_L[x][y] = (sum(py) + 8) >> 4
            elif all_satisfy(px, lambda n:n != None) and any_satisfy(py, lambda n:n == None):
                pred_L[x][y] = (sum(px) + 8) >> 4
            else:
                pred_L[x][y] = (1 << (mb.slice.BitDepth_Y - 1))
    return pred_L

# 8.3.3.4 Specification of Intra_16x16_Plane prediction mode
def pred16x16_P(p, mb):
    pred_L = array_2d(16,16)
    H = sum([(x+1)*(p[9+x][0] - p[7-x][0]) for x in range(8)])
    V = sum([(y+1)*(p[0][9+y] - p[0][7-y]) for y in range(8)])
    for x in range(16):
        for y in range(16):
            a = 16 * (p[0][16] + p[16][0])
            b = (5 * H + 32) >> 6
            c = (5 * V + 32) >> 6
            pred_L[x][y] = Clip1_Y((a + b * (x - 7) + c * (y - 7) + 16) >> 5, mb.slice.sps.BitDepth_Y)
    return pred_L

# 8.3.4 Intra prediction process for chroma samples
def chroma_pred(mb):
    for iCbCr in [1, 2]:
        chroma_pred_C(mb, iCbCr)
        idct.idct_for_chroma_C(mb, iCbCr)

def chroma_pred_C(mb, iCbCr):
    assert iCbCr in [1, 2]
    mbs = mb.slice.mbs
    if mb.slice.sps.ChromaArrayType == 3:
        raise NameError("Chroma Array Type 3 not impl")
    else:
        p = array_2d(mb.slice.sps.MbWidthC+1, mb.slice.sps.MbHeightC+1)
        for x in range(-1, mb.slice.sps.MbWidthC):
            ys = range(-1, mb.slice.sps.MbHeightC) if x == -1 else [-1]
            for y in ys:
                (mbAddrN, xW, yW) = mb.chroma_neighbor_location(x, y)
                if mbAddrN == None or \
                   ("Inter" in mbs[mbAddrN].pred_mode and mbs[mbAddrN].constrained_intra_pred_flag == 1):
                    p[x+1][y+1] = None
                else:
                    mbN = mbs[mbAddrN]
                    MbaffFrameFlag = mbN.slice.MbaffFrameFlag
                    PicWidthInSamples_L = mbN.slice.PicWidthInSamples_L
                    (xL, yL) = get_cord_of_mb(mbAddrN, MbaffFrameFlag, PicWidthInSamples_L)
                    xM = (xL >> 4) * mbN.slice.sps.MbWidthC
                    yM = ((yL >> 4) * mbN.slice.sps.MbHeightC) + (yL % 2)
                    if MbaffFrameFlag == 0:
                        if iCbCr == 1:
                            p[x+1][y+1] = mbN.slice.S_prime_Cb[xM+xW][yM+yW]
                        elif iCbCr == 2:
                            p[x+1][y+1] = mbN.slice.S_prime_Cr[xM+xW][yM+yW]
                    else:
                        raise NameError("Field mb may exist")
    pred_chroma_fn = [pred_chroma_DC, pred_chroma_H,pred_chroma_V,pred_chroma_P][mb.intra_chroma_pred_mode]
    if iCbCr == 1:
        mb.pred_Cb = pred_chroma_fn(p, mb)
        # print(mb.idx, iCbCr, "preded", mb.pred_Cb)
    elif iCbCr == 2:
        mb.pred_Cr = pred_chroma_fn(p, mb)
        # print(mb.idx, iCbCr, "preded", mb.pred_Cr)

# 8.3.4.1 Specification of Intra_Chroma_DC prediction mode
def pred_chroma_DC(p, mb):
    pred_C = array_2d(mb.slice.sps.MbWidthC, mb.slice.sps.MbHeightC)
    for blkIdx in range(1 << (mb.slice.sps.ChromaArrayType + 1)):
        (xO, yO) = get_cord_of_chroma4x4(blkIdx)
        pxs = [p[x+xO+1][0] for x in range(4)]
        pys = [p[0][y+yO+1] for y in range(4)]
        if (xO, yO) == (0, 0) or (xO > 0 and yO > 0):
            for x in range(4):
                for y in range(4):
                    if all_satisfy(pxs, lambda n:n != None) and all_satisfy(pys, lambda n:n != None):
                        pred_C[x+xO][y+yO] = (sum(pxs) + sum(pys)) >> 3
                    elif any_satisfy(pxs, lambda n:n == None) and all_satisfy(pys, lambda n:n != None):
                        pred_C[x+xO][y+yO] = (sum(pys) + 2) >> 2
                    elif all_satisfy(pxs, lambda n:n != None) and any_satisfy(pys, lambda n:n == None):
                        pred_C[x+xO][y+yO] = (sum(pxs) + 2) >> 2
                    else:
                        pred_C[x+xO][y+yO] = (1 << (mb.slice.sps.BitDepth_C - 1))
        elif xO > 0 and yO == 0:
            for x in range(4):
                for y in range(4):
                    if all_satisfy(pxs, lambda n:n != None):
                        pred_C[x+xO][y+yO] = (sum(pxs) + 2) >> 2
                    elif all_satisfy(pys, lambda n:n != None):
                        pred_C[x+xO][y+yO] = (sum(pys) + 2) >> 2
                    else:
                        pred_C[x+xO][y+yO] = (1 << (mb.slice.sps.BitDepth_C - 1))
        else:
            for x in range(4):
                for y in range(4):
                    if all_satisfy(pys, lambda n:n != None):
                        pred_C[x+xO][y+yO] = (sum(pys) + 2) >> 2
                    elif all_satisfy(pxs, lambda n:n != None):
                        pred_C[x+xO][y+yO] = (sum(pxs) + 2) >> 2
                    else:
                        pred_C[x+xO][y+yO] = (1 << (mb.slice.sps.BitDepth_C - 1))
    return pred_C

# 8.3.4.2 Specification of Intra_Chroma_Horizontal prediction mode
def pred_chroma_H(p, mb):
    pred_C = array_2d(mb.slice.sps.MbWidthC, mb.slice.sps.MbHeightC)
    for x in range(mb.slice.sps.MbWidthC):
        for y in range(mb.slice.sps.MbHeightC):
            pred_C[x][y] = p[0][y+1]
    return pred_C

# 8.3.4.3 Specification of Intra_Chroma_Vertical prediction mode
def pred_chroma_V(p, mb):
    pred_C = array_2d(mb.slice.sps.MbWidthC, mb.slice.sps.MbHeightC)
    for x in range(mb.slice.sps.MbWidthC):
        for y in range(mb.slice.sps.MbHeightC):
            pred_C[x][y] = p[x+1][0]
    return pred_C

# 8.3.4.4 Specification of Intra_Chroma_Plane prediction mode
def pred_chroma_P(p, mb):
    pred_C = array_2d(mb.slice.sps.MbWidthC, mb.slice.sps.MbHeightC)
    xCF = 4 if mb.slice.sps.ChromaArrayType == 3 else 0
    yCF = 4 if mb.slice.sps.ChromaArrayType != 1 else 0
    H = sum([(x+1)*(p[5+xCF+x][0] - p[3+xCF-x][0]) for x in range(4+xCF)])
    V = sum([(y+1)*(p[0][5+yCF+y] - p[0][3+yCF-y]) for y in range(4+yCF)])
    a = 16 * (p[0][mb.slice.sps.MbHeightC] + p[mb.slice.sps.MbWidthC][0])
    b = ((34 - 29 * (mb.slice.sps.ChromaArrayType == 3 )) * H + 32) >> 6
    c = ((34 - 29 * (mb.slice.sps.ChromaArrayType != 1 )) * V + 32) >> 6
    for x in range(mb.slice.sps.MbWidthC):
        for y in range(mb.slice.sps.MbHeightC):
            pred_C[x][y] = Clip1_C((a + b * (x - 3 - xCF) + c * (y - 3 - yCF) + 16) >> 5, mb.slice.sps.BitDepth_C)
    return pred_C

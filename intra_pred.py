from utilities import get_cord_of_luma4x4, get_cord_of_mb, all_satisfy, any_satisfy, array_2d, pic_paint
from pprint import pprint
import idct
# 8.3 Intra prediction process

def intra_pred(mb):
    print("decoding mb ", mb.idx)
    MvCnt = 0
    for blk in mb.luma_blocks:
        print("  blk ", blk.idx)
        if blk.color == "Y":
            if blk.mb.pred_mode == "Intra4x4":
                intra_4x4_luma(blk)
            elif blk.mb.pred_mode == "Intra8x8":
                raise NameError("8x8 not impl")
            else:
                raise NameError("16x16 not impl")
                # pred_L = intra_16x16_luma(S_prime_L)
        else:
            raise NameError("8.3.4")

# 8.3.1 Intra_4x4 prediction process for luma samples
def intra_4x4_luma(blk):
    gen_intra_4x4_pred_mode(blk)
    gen_pred4x4_L(blk)
    (xO, yO) = get_cord_of_luma4x4(blk.idx)
    # blk.pred_L = array_2d(4,4)
    for x in range(4):
        for y in range(4):
            blk.mb.pred_L[xO+x][yO+y] = blk.pred4x4_L[x][y]
    # print("Pred_L:", blk.mb.pred_L)
    idct.construct_picture(blk)
    # pic_paint(blk.mb.slice.S_prime_L)

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
    print("Intra4x4PredMode:", ["V", "H", "DC", "DDL","DDR", "VR", "HD", "VL", "HU"][blk.Intra4x4PredMode])

# 8.3.1.2 Intra_4x4 sample prediction -> pred4x4_L
def gen_pred4x4_L(blk):
    mbs = blk.mb.slice.mbs
    (xO, yO) = get_cord_of_luma4x4(blk.idx)
    p = array_2d(5,9)
    for y in  range(-1,4):
        xs = range(-1,8) if y == -1 else [-1]
        for x in xs:
            xN = xO + x
            yN = yO + y
            (mbAddrN, xW, yW) = blk.luma_neighbor_location(xN, yN)
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
def intra_16x16_luma():
    assert False

# 8.3.3.1 Specification of Intra_16x16_Vertical prediction mode
def pred16x16_V():
    assert False
# 8.3.3.2 Specification of Intra_16x16_Horizontal prediction mode
def pred16x16_H():
    assert False
# 8.3.3.3 Specification of Intra_16x16_DC prediction mode
def pred16x16_DC():
    assert False
# 8.3.3.4 Specification of Intra_16x16_Plane prediction mode
def pred16x16_P():
    assert False

# 8.3.4 Intra prediction process for chroma samples
# 8.3.4.1 Specification of Intra_Chroma_DC prediction mode
# 8.3.4.2 Specification of Intra_Chroma_Horizontal prediction mode
# 8.3.4.3 Specification of Intra_Chroma_Vertical prediction mode
# 8.3.4.4 Specification of Intra_Chroma_Plane prediction mode

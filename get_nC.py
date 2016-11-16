#9.2.1
def get_nC():
    if mode = "ChromaDCLevel":
        if ChromaArrayType == 1:
            return -1
        elif:
            return -2
    else:
        #1
        if mode == "Intra16x16DCLevel":
            luma4x4BlkIdx = 0
        #2
        elif mode == "CbIntra16x16DCLevel":
            cb4x4BlkIdx = 0
        #3
        elif mode == "CrIntra16x16DCLevel":
            cr4x4BlkIdx = 0
        #4
        if mode in ["Intra16x16DCLevel", "Intra16x16ACLevel", "LumaLevel4x4"]:
            (mbAddrA, mbAddrB, luma4x4BlkIdxA, luma4x4BlkIdxB) = get_neighbor(luma4x4BlkIdx)
            blkA = (mbAddrA, luma4x4BlkIdxA)
            blkB = (mbAddrB, luma4x4BlkIdxB)
        elif mode in ["CbIntra16x16DCLevel", "CbIntra16x16ACLevel", "CbLevel4x4"]:
            assert True
        elif mode in ["CrIntra16x16DCLevel", "CrIntra16x16ACLevel", "CrLevel4x4"]:
            assert True
        elif mode == "ChromaACLevel"
            assert True
        #5
        if mbAddrA == None or \
           False: #"constrained_intra_pred_flag" == 1 ...
            availableFlagA = 0
        else:
            availableFlagA = 1
        if mbAddrB == None or \
           False: #"constrained_intra_pred_flag" == 1 ...
            availableFlagB = 0
        else:
            availableFlagB = 1
        #6
        if availableFlagA == 1:
            if mb[mbAddrA].mb_type in ["P_Skip", "B_Skip"]: #or \
               #The macroblock mbAddrN has mb_type not equal to I_PCM and all AC residual transform coefficient levels of the neighbouring block blkN are equal to 0 due to the corresponding bit of CodedBlockPatternLuma or CodedBlockPatternChroma being equal to 0.
                nA = 0
            elif False: # mbAddrN is I_PCM
                nA = 16
            else:
                nA = #TotalCoeff( coeff_token ) of the neighbouring block blkN
        if availableFlagB == 1:
            if mb[mbAddrB].mb_type in ["P_Skip", "B_Skip"]: #or \
               #The macroblock mbAddrN has mb_type not equal to I_PCM and all AC residual transform coefficient levels of the neighbouring block blkN are equal to 0 due to the corresponding bit of CodedBlockPatternLuma or CodedBlockPatternChroma being equal to 0.
                nB = 0
            elif False: # mbAddrN is I_PCM
                nB = 16
            else:
                nB = #TotalCoeff( coeff_token ) of the neighbouring block blkN
        #7
        if availableFlagA == 1 and availableFlagB == 1:
            nC = ( nA + nB + 1 ) >> 1
        elif availableFlagA == 1 and availableFlagB == 0:
            nC = nA
        elif availableFlagA == 0 and availableFlagB == 1:
            nC = nB
        else:
            nC = 0 

def get_neighbor(luma4x4BlkIdx):
    #6.4.11.4
    # A:
    #1
    (xD, yD) = (-1, 0)
    #2 -> 6.4.3
    x = InverseRasterScan( luma4x4BlkIdx / 4, 8, 8, 16, 0 ) + InverseRasterScan( luma4x4BlkIdx % 4, 4, 4, 8, 0 )
    y = InverseRasterScan( luma4x4BlkIdx / 4, 8, 8, 16, 1 ) + InverseRasterScan( luma4x4BlkIdx % 4, 4, 4, 8, 1 )
    #3
    (xN, yN) = (x + xD, y + yD)
    #4 -> 6.4.12 : (xN, yN) -> mbAddrN, (xW, yW)
    if mode == "Luma":
        maxW = 16
        maxH = 16
    elif mode == "Chroma":
        maxW = MbWidthC
        maxH = MbHeightC
    if MbaffFrameFlag == 0:
        #6.4.12.1
        mbAddrN = table6_3(xN, yN)
        xW = ( xN + maxW ) % maxW
        yW = ( yN + maxH ) % maxH
    else:
        #6.4.12.2

    #5
    if mbAddrA == None:
        luma4x4BlkIdxA = None
    else:
        #6.4.13.1

    pass

def InverseRasterScan(a, b, c, d, e):
    if e == 0:
        (a % ( d / b ) ) * b
    elif e == 1:
        (a / ( d / b ) ) * c
    else:
        assert False

def 
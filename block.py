def InverseRasterScan(a, b, c, d, e):
    if e == 0:
        return (a % ( d // b ) ) * b
    elif e == 1:
        return (a // ( d // b ) ) * c
    else:
        assert False

def all_ac_zeros(xs):
    for x in xs[1:]:
        if x != 0:
            return False
    return True

class Block:

    def __init__(self, idx, mode, mb):
        self.idx = idx
        self.mode = mode
        self.mb = mb
        self.slice = mb.slice
        self.bits = self.mb.slice.bits

    def parse(self, startIdx, endIdx, maxNumCoeff):
        self.coeffLevel = self.parse_cavlc(startIdx, endIdx, maxNumCoeff)

    def parse_cavlc(self, startIdx, endIdx, maxNumCoeff):
        # decode one block in macroblock
        print("  Start decoding block ", self.idx)
        coeffLevel = [None] * maxNumCoeff
        for i in range(maxNumCoeff):
            coeffLevel[i] = 0

        nC = self.ce_nc()
        self.nC = nC
        (TrailingOnes, TotalCoeff, coeff_token) = self.bits.ce_coeff_token(nC)
        print("    T1s,Tc, token:",TrailingOnes, TotalCoeff, coeff_token)
        self.coeff_token = coeff_token
        self.TrailingOnes = TrailingOnes
        self.TotalCoeff = TotalCoeff
        if TotalCoeff > 0:
            if TotalCoeff > 10 and TrailingOnes < 3:
                suffixLength = 1
            else:
                suffixLength = 0
            levelVal = [None] * TotalCoeff
            for i in range(TotalCoeff):
                if i < TrailingOnes:
                    trailing_ones_sign_flag = self.bits.u(1)
                    print("    trailing_ones_sign_flag:", trailing_ones_sign_flag)
                    levelVal[i] = 1 - 2 * trailing_ones_sign_flag
                else:
                    level_prefix = self.bits.ce_level_prefix()
                    print("    level_prefix:", level_prefix)
                    if level_prefix == 14 and suffixLength == 0:
                        levelSuffixSize = 4
                    elif level_prefix >= 15:
                        levelSuffixSize = level_prefix - 3
                    else:
                        levelSuffixSize = suffixLength

                    levelCode = (min(15, level_prefix) << suffixLength)
                    if suffixLength > 0 or level_prefix >= 14:
                        if levelSuffixSize > 0:
                            level_suffix = self.bits.u(levelSuffixSize)
                            print("    level_suffix:", level_suffix, "length:", suffixLength)
                        else:
                            level_suffix = 0
                        levelCode += level_suffix
                    if level_prefix > 15 and suffixLength == 0:
                        levelCode += 15
                    if level_prefix >= 16:
                        levelCode += (1 << (level_prefix - 3)) - 4096
                    if i == TrailingOnes and TrailingOnes < 3:
                        levelCode += 2
                    if levelCode % 2 == 0:
                        levelVal[i] = (levelCode + 2) >> 1
                    else:
                        levelVal[i] = (-levelCode - 1) >> 1
                    if suffixLength == 0:
                        suffixLength = 1
                    if abs(levelVal[i]) > (3 << (suffixLength - 1)) and suffixLength < 6:
                        suffixLength += 1
            # if TotalCoeff < endIdx - startIdx + 1 :
            if TotalCoeff < maxNumCoeff:
                tzVlcIndex = TotalCoeff
                total_zeros = self.bits.ce_total_zeros(tzVlcIndex,maxNumCoeff)
                print("    ce_total_zeros,tzVlc,maxNumCoeff:", total_zeros, tzVlcIndex, maxNumCoeff)
                zerosLeft = total_zeros
            else:
                zerosLeft = 0
            runVal = [None] * TotalCoeff
            for i in range(TotalCoeff - 1):
                if zerosLeft > 0:
                    run_before = self.bits.ce_run_before(zerosLeft)
                    print("    run_before, zero_left:", run_before, zerosLeft)
                    runVal[i] = run_before
                else:
                    runVal[i] = 0
                zerosLeft = zerosLeft - runVal[i]
            runVal[TotalCoeff - 1] = zerosLeft
            coeffNum = -1
            for i in reversed(range(TotalCoeff)):
                coeffNum += runVal[i] + 1
                coeffLevel[startIdx + coeffNum] = levelVal[i]
        print("    Decoded Luma Block:", coeffLevel)
        return coeffLevel

    def dump_mbs(self):
        print("DUMP MBS:")
        for mb in self.slice.mbs:
            print("\n")
            for blk in mb.luma_blocks:
                try:
                    print(blk.TotalCoeff)
                except:
                    pass

    def ce_nc(self):
        mode = self.mode
        luma4x4BlkIdx = self.idx #block_param["luma4x4BlkIdx"]
        if "ChromaDCLevel" in mode:
            if self.slice.sps["ChromaArrayType"] == 1:
                return -1
            else:
                return -2
        else:
            if mode == "Intra16x16DCLevel":
                luma4x4BlkIdx = 0
            elif mode == "CbIntra16x16DCLevel":
                cb4x4BlkIdx = 0
            elif mode == "CrIntra16x16DCLevel":
                cr4x4BlkIdx = 0
            if mode in ["Intra16x16DCLevel", "Intra16x16ACLevel", "LumaLevel4x4"]:
                (mbAddrA, luma4x4BlkIdxA) = self.neighbor("A")
                print("      BLOCK A:",mbAddrA, luma4x4BlkIdxA)
                blkA = None if mbAddrA == None else self.slice.mbs[mbAddrA].luma_blocks[luma4x4BlkIdxA]
                (mbAddrB, luma4x4BlkIdxB) = self.neighbor("B")
                print("      BLOCK B:",mbAddrB, luma4x4BlkIdxB)
                blkB = None if mbAddrB == None else self.slice.mbs[mbAddrB].luma_blocks[luma4x4BlkIdxB]
            elif mode in ["CbIntra16x16DCLevel", "CbIntra16x16ACLevel", "CbLevel4x4"]:
                raise NameError("Cb not impl")
            elif mode in ["CrIntra16x16DCLevel", "CrIntra16x16ACLevel", "CrLevel4x4"]:
                raise NameError("Cr not impl")
            elif mode == "ChromaACLevel":
                raise NameError("ChromaAC not impl")
            #5
            availableFlagA = 0 if mbAddrA == None else 1
            availableFlagB = 0 if mbAddrB == None else 1
            #6
            if availableFlagA == 1:
                if self.slice.mbs[mbAddrA].mb_type in ["P_Skip", "B_Skip"] or \
                        (self.slice.mbs[mbAddrA].mb_type != "I_PCM" and all_ac_zeros(blkA.coeffLevel)):
                    # ALERT ERROR PRONE
                    nA = 0
                else:
                    nA = blkA.TotalCoeff
            if availableFlagB == 1:
                if self.slice.mbs[mbAddrB].mb_type in ["P_Skip", "B_Skip"] or \
                        (self.slice.mbs[mbAddrB].mb_type != "I_PCM" and all_ac_zeros(blkB.coeffLevel)):
                    # ALERT ERROR PRONE
                    nB = 0
                else:
                    nB = blkB.TotalCoeff
            #7
            if availableFlagA == 1 and availableFlagB == 1:
                nC = ( nA + nB + 1 ) >> 1
            elif availableFlagA == 1 and availableFlagB == 0:
                nC = nA
            elif availableFlagA == 0 and availableFlagB == 1:
                nC = nB
            else:
                nC = 0
            return nC

    def neighbor(self, direct):
        # 6.4.11.4
        shiftTable = {"A":(-1,0), "B":(0,-1), "C":("predPartWidth",-1), "D":(-1,-1)}
        mode = self.mode
        luma4x4BlkIdx = self.idx
        res = []
        (xD, yD) = shiftTable[direct]
        x = InverseRasterScan( luma4x4BlkIdx // 4, 8, 8, 16, 0 ) + \
            InverseRasterScan( luma4x4BlkIdx % 4, 4, 4, 8, 0 )
        y = InverseRasterScan( luma4x4BlkIdx // 4, 8, 8, 16, 1 ) + \
            InverseRasterScan( luma4x4BlkIdx % 4, 4, 4, 8, 1 )
        (xN, yN) = (x + xD, y + yD) #3
        if "Luma" in mode:
            maxW = 16
            maxH = 16
        elif "Chroma" in mode:
            raise NameError("Chroma Not impl")
            maxW = MbWidthC
            maxH = MbHeightC
        if self.slice.var["MbaffFrameFlag"] == 0:
            tmp = self.belongMB(xN, yN, maxW, maxH)
            if tmp == "A":
                mbAddrTmp = self.slice.var["CurrMbAddr"] - 1
                if mbAddrTmp < 0 or mbAddrTmp > self.slice.var["CurrMbAddr"] or self.slice.var["CurrMbAddr"] % self.slice.var["PicWidthInMbs"] == 0:
                    mbAddrTmp = None
            elif tmp == "B":
                mbAddrTmp = self.slice.var["CurrMbAddr"] - self.slice.var["PicWidthInMbs"]
                if mbAddrTmp < 0 or mbAddrTmp > self.slice.var["CurrMbAddr"]:
                    mbAddrTmp = None
            elif tmp == "X":
                mbAddrTmp = self.slice.var["CurrMbAddr"]
            elif tmp == "C":
                mbAddrTmp = self.slice.var["CurrMbAddr"] - self.slice.var["PicWidthInMbs"] + 1
                if mbAddrTmp < 0 or mbAddrTmp > self.slice.var["CurrMbAddr"] or self.slice.var["CurrMbAddr"]+1 % self.slice.var["PicWidthInMbs"] == 0:
                    mbAddrTmp = None
            elif tmp == "D":
                mbAddrTmp = self.slice.var["CurrMbAddr"] - self.slice.var["PicWidthInMbs"] - 1
                if mbAddrTmp < 0 or mbAddrTmp > self.slice.var["CurrMbAddr"] or self.slice.var["CurrMbAddr"] % self.slice.var["PicWidthInMbs"] == 0:
                    mbAddrTmp = None
            else:
                raise NameError("direction impossible")
            xW = ( xN + maxW ) % maxW
            yW = ( yN + maxH ) % maxH
        else:
            # 6.4.12.2
            raise NameError("6.4.12.2 not impl")
        if mbAddrTmp == None:
            luma4x4BlkIdxTmp = None
        else:
            luma4x4BlkIdxTmp = int(8 * ( yW // 8 ) + 4 * ( xW // 8 ) + 2 * ( ( yW % 8 ) // 4 ) + ( ( xW % 8 ) // 4 ))
        # print("      Find neighbor:", direct)
        # print("      xD, yD:", xD, yD)
        # print("      x, y:", x, y)
        # print("      xN, yN:", xN, yN)
        # print("      xW, yW:", xW, yW)
        # print("      mbAddrN:", tmp, mbAddrTmp)
        # print("      lumaIdx:", luma4x4BlkIdxTmp)
        return (mbAddrTmp, luma4x4BlkIdxTmp)


    def belongMB(self, xN, yN, maxW, maxH):
        # find the mb which neighbour belongs to
        if xN < 0 and yN < 0:
            return "D"
        if xN < 0 and (0 <= yN and yN <= maxH-1):
            return "A"
        if (0 <= xN and xN <= maxW-1) and yN < 0:
            return "B"
        if (0 <= xN and xN <= maxW-1) and (0 <= yN and yN <= maxH-1):
            return "X"
        if xN > maxW - 1 and yN < 0:
            return "C"
        if xN > maxW - 1 and (0 <= yN and yN <= maxH-1):
            return None
        if yN > maxH-1:
            return None

    def check_mb_avail(self, mbAddr):
        if mbAddr < 0 or mbAddr > self.slice.var["CurrMbAddr"]:
            return None
        else:
            return mbAddr

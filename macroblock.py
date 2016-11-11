from pprint import pprint

class Macroblock:
    mb_type = {
        0: "I_NxN"
    }

    def __init__(self, parent_slice):
        self.slice = parent_slice
        self.params = {}
        self.var = {}
        self.parse()

    def parse(self):
        print("MacroBlock:")
        self.init_params()
        self.macroblock_layer()

    def init_params(self):
        self.params["transform_size_8x8_flag"] = 0
        self.params["prev_intra4x4_pred_mode_flag"] = [None]*16
        self.params["prev_intra8x8_pred_mode_flag"] = [None]*16
        self.params["rem_intra4x4_pred_mode"] = [None]*16
        self.params["rem_intra8x8_pred_mode"] = [None]*16

    def macroblock_layer(self) :
        self.params["mb_type_int"] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.ue()
        self.params["mb_type"] = Macroblock.mb_type[self.params["mb_type_int"]]
        if self.params["mb_type"] == "I_PCM" :
            print("I_PCM Not Impl")
            # while not self.slice.bits.byte_aligned() :
            #     self.params["pcm_alignment_zero_bit"] = self.slice.bits.f(1)
            # for i in range(256) :
            #     self.params["pcm_sample_luma"][i] = self.slice.bits.u(v)
            # for i in (2 * MbWidthC * MbHeightC) :
            #     self.params["pcm_sample_chroma"][i] = self.slice.bits.u(v)
        else :
            noSubMbPartSizeLessThan8x8Flag = 1
            if self.params["mb_type"] != "I_NxN" and \
               MbPartPredMode(self.params["mb_type_int"], 0) != "Intra_16x16" and \
               NumMbPart(self.params["mb_type"]) == 4 :
                print("mb 41: not Impl")
                pass
                # sub_mb_pred(self.params["mb_type"])
                # for mbPartIdx in range(4) :
                #     if sub_self.params["mb_type"][mbPartIdx] != "B_Direct_8x8" :
                #         if NumSubMbPart(sub_self.params["mb_type"][mbPartIdx] > 1 :
                #             noSubMbPartSizeLessThan8x8Flag = 0
                #     elif not direct_8x8_inference_flag :
                #         noSubMbPartSizeLessThan8x8Flag = 0
            else :
                if self.slice.pps["transform_8x8_mode_flag"] and self.params["mb_type"] == "I_NxN" :
                    self.params["transform_size_8x8_flag"] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.u(1)
                self.mb_pred(self.params["mb_type_int"])
            if self.MbPartPredMode(self.params["mb_type_int"], 0) != "Intra_16x16" :
                self.params["coded_block_pattern"] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.me(self.MbPartPredMode(self.params["mb_type_int"], 0))
                if self.params["mb_type"] == "I_NxN":
                    self.var["CodedBlockPatternLuma"] = self.params["coded_block_pattern"] % 16
                    self.var["CodedBlockPatternChroma"] = self.params["coded_block_pattern"] / 16
                else:
                    print("CodedBlockPatternLuma/Chroma not derived!!!!")
                if self.var["CodedBlockPatternLuma"] > 0 and \
                   self.slice.pps["transform_8x8_mode_flag"] and \
                   self.params["mb_type"] != "I_NxN" and \
                   noSubMbPartSizeLessThan8x8Flag and \
                   (self.params["mb_type"] != "B_Direct_16x16" or self.params["direct_8x8_inference_flag"]) :
                    self.params["transform_size_8x8_flag"] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.u(1)
            if self.var["CodedBlockPatternLuma"] > 0 or self.var["CodedBlockPatternChroma"] > 0 or \
               self.MbPartPredMode(self.params["mb_type_int"], 0) == "Intra_16x16" :
                self.params["mb_qp_delta"] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.se()
                pprint(self.params)
                self.residual(0, 15)

    def MbPartPredMode(self, mb_type, n):
        assert n == 0
        if mb_type == 0 and self.params["transform_size_8x8_flag"] == 0:
            return "Intra_4x4"
        elif mb_type == 0 and self.params["transform_size_8x8_flag"] == 1:
            return "Intra_8x8"
        else:
            print("MbPartPredMode Not Impl")

    def mb_pred(self, mb_type):
        if self.MbPartPredMode(mb_type, 0) == "Intra_4x4" or \
           self.MbPartPredMode(mb_type, 0) == "Intra_8x8" or \
           self.MbPartPredMode(mb_type, 0) == "Intra_16x16":
            if self.MbPartPredMode(mb_type, 0) == "Intra_4x4":
                for luma4x4BlkIdx in range(16):
                    self.params["prev_intra4x4_pred_mode_flag"][luma4x4BlkIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.u(1)
                    if not self.params["prev_intra4x4_pred_mode_flag"][luma4x4BlkIdx]:
                        self.params["rem_intra4x4_pred_mode"][luma4x4BlkIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.u(3)
            if self.MbPartPredMode(mb_type,0) == "Intra_8x8":
                for luma8x8BlkIdx in range(4):
                    self.params["prev_intra8x8_pred_mode_flag"][luma8x8BlkIdx] =self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.u(1) 
                    if not self.params["prev_intra8x8_pred_mode_flag"][luma8x8BlkIdx]:
                        self.params["rem_intra8x8_pred_mode"][luma8x8BlkIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.u(3)
            if self.slice.sps["ChromaArrayType"] == 1 or self.slice.sps["ChromaArrayType"] == 2: 
                self.params["intra_chroma_pred_mode"] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.ue()
        elif self.MbPartPredMode(mb_type, 0) != "Direct":
            for mbPartIdx in range(NumMbPart(mb_type)):
                if self.params["num_ref_idx_l0_active_minus1"] > 0 or \
                   self.params["mb_field_decoding_flag"] != self.params["field_pic_flag"] and \
                   self.MbPartPredMode(mb_type, mbPartIdx) != "Pred_L1":
                    self.params["ref_idx_l0"][mbPartIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.te()
            for mbPartIdx in range(NumMbPart(mb_type)):
                if self.params["num_ref_idx_l1_active_minus1"] > 0 or \
                   self.params["mb_field_decoding_flag"] != self.params["field_pic_flag"] and \
                   self.MbPartPredMode(mb_type, mbPartIdx ) != "Pred_L0":
                    self.params["ref_idx_l1"][mbPartIdx] =self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.te()
            for mbPartIdx in range(NumMbPart(mb_type)):
                if self.MbPartPredMode(mb_type, mbPartIdx ) != "Pred_L1":
                    for compIdx in range(2):
                        self.params["mvd_l0"][mbPartIdx][0][compIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.se()
            for mbPartIdx in range(NumMbPart(mb_type)):
                if self.MbPartPredMode(mb_type, mbPartIdx ) != "Pred_L0":
                    for compIdx in range(2):
                        self.params["mvd_l1"][mbPartIdx][0][compIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.se()

    def residual(self, startIdx, endIdx):
        if not self.slice.pps["entropy_coding_mode_flag"]:
            self.residual_block = self.residual_block_cavlc
        else:
            self.residual_block = self.residual_block_cabac
        (Intra16x16DCLevel, Intra16x16ACLevel, LumaLevel4x4, LumaLevel8x8) = \
            self.residual_luma(startIdx, endIdx)
        if self.slice.sps["ChromaArrayType"] == 1 or self.slice.sps["ChromaArrayType"] == 2:
            print("mb 128 not impl")
        elif self.slice.sps["ChromaArrayType"] == 3:
            print("mb 130 not impl")

    def residual_luma(startIdx, endIdx):
        i16x16DClevel = [None] * 16
        i16x16AClevel = [[None] * 16] * 16
        # level4x4
        # level8x8
        if startIdx == 0 and \
           self.MbPartPredMode(self.params["mb_type_int"], 0) == "Intra_16x16":
            self.residual_block(i16x16DClevel, 0, 15, 16)
        for i8x8 in range(4):
            if not self.params["transform_size_8x8_flag"] or \
               not self.slice.pps["entropy_coding_mode_flag"]:
                for i4x4 in range(4):
                    if self.var["CodedBlockPatternLuma"] & (1 << i8x8):
                        if self.MbPartPredMode(self.params["mb_type_int"], 0) == "Intra_16x16":
                            self.residual_block( i16x16AClevel[i8x8 * 4 + i4x4], max(0, startIdx - 1), endIdx - 1, 15)
                        else:
                            self.residual_block(level4x4[i8x8 * 4 + i4x4], startIdx, endIdx, 16)
                    elif self.MbPartPredMode(self.params["mb_type_int"], 0) == "Intra_16x16":
                        for i in range(15):
                            i16x16AClevel[i8x8 * 4 + i4x4][i] = 0
                    else:
                        for i in range(16):
                            level4x4[i8x8 * 4 + i4x4][i] = 0
                    if not self.slice.pps["entropy_coding_mode_flag"] and \
                       self.params["transform_size_8x8_flag"]:
                        for i in range(16):
                            level8x8[ i8x8 ][ 4 * i + i4x4 ] = level4x4[ i8x8 * 4 + i4x4 ][ i ]
            elif CodedBlockPatternLuma & ( 1 << i8x8 ):
                self.residual_block( level8x8[ i8x8 ], 4 * startIdx, 4 * endIdx + 3, 64 )
            else:
                for i in range(64):
                    level8x8[ i8x8 ][ i ] = 0

    def residual_block_cavlc(coeffLevel, startIdx, endIdx, maxNumCoeff):
        coeffLevel = [None] * maxNumCoeff
        for i in range(maxNumCoeff):
            coeffLevel[i] = 0
        coeff_token = self.bits.ce()
        if TotalCoeff(coeff_token) > 0:
            if TotalCoeff(coeff_token) > 10 and TrailingOnes(coeff_token) < 3:
                suffixLength = 1
            else:
                suffixLength = 0
            for i in range(TotalCoeff(coeff_token)):
                if i < TrailingOnes(coeff_token):
                    trailing_ones_sign_flag = self.bits.u(1)
                    levelVal[i] = 1 - 2 * trailing_ones_sign_flag
                else:
                    level_prefix = self.bits.ce()
                    levelCode = (min(15, level_prefix) << suffixLength)
                    if suffixLength > 0 or level_prefix >= 14:
                        level_suffix = self.u(v)
                        levelCode + level_suffix
                    if level_prefix > 15 and suffixLength == 0:
                        levelCode += 15
                    if level_prefix >= 16:
                        levelCode += (1 << (level_prefix - 3)) - 4096
                    if i == TrailingOnes(coeff_token) and TrailingOnes(coeff_token) < 3:
                        levelCode += 2
                    if levelCode % 2 == 0:
                        levelVal[i] = (levelCode + 2) >> 1
                    else:
                        levelVal[i] = (-levelCode - 1) >> 1
                    if suffixLength == 0:
                        suffixLength = 1
                    if abs(levelVal[i]) > (3 << (suffixLength - 1)) and suffixLength < 6:
                        suffixLength += 1
            if TotalCoeff(coeff_token) < endIdx - startIdx + 1 :
                total_zeros = self.bits.ce()
                zerosLeft = total_zeros
            else:
                zerosLeft = 0
            for i in range(TotalCoeff(coeff_token) - 1):
                if zerosLeft > 0:
                    run_before = self.bits.ce()
                    runVal[i] = run_before
                else:
                    runVal[i] = 0
                zerosLeft = zerosLeft - runVal[i]
            runVal[TotalCoeff(coeff_token) - 1] = zerosLeft
            coeffNum = -1
            for i in revese(range(TotalCoeff(coeff_token))):
                coeffNum += runVal[i] + 1
                coeffLevel[startIdx + coeffNum] = levelVal[i]

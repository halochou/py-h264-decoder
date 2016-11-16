from block import Block
from pprint import pprint

mbtype_islice_table = ["I_NxN","I_16x16_0_0_0","I_16x16_1_0_0","I_16x16_2_0_0","I_16x16_3_0_0","I_16x16_0_1_0","I_16x16_1_1_0","I_16x16_2_1_0","I_16x16_3_1_0","I_16x16_0_2_0","I_16x16_1_2_0","I_16x16_2_2_0","I_16x16_3_2_0","I_16x16_0_0_1","I_16x16_1_0_1","I_16x16_2_0_1","I_16x16_3_0_1","I_16x16_0_1_1","I_16x16_1_1_1","I_16x16_2_1_1","I_16x16_3_1_1","I_16x16_0_2_1","I_16x16_1_2_1","I_16x16_2_2_1","I_16x16_3_2_1","I_PCM"]


class Macroblock:

    def __init__(self, parent_slice):
        self.slice = parent_slice
        self.params = {}
        self.var = {}
        self.mb_type_int = self.slice.bits.ue()
        if self.slice.params["slice_type"] == "I":
            self.mb_type = mbtype_islice_table[self.mb_type_int]
        else:
            raise NameError("Unknow MB Type")
        self.pred_mode = self.MbPartPredMode(self.mb_type_int)
        self.luma_blocks = []
        if self.pred_mode == "Intra_4x4":
            for i in range(16):
                self.luma_blocks.append(Block(i, "LumaLevel4x4", self))
        elif self.pred_mode == "Intra_8x8":
            for i in range(4):
                self.luma_blocks.append(Block(i, "LumaLevel8x8", self))
        elif self.pred_mode == "Intra_16x16":
            self.luma_i16x16_dc_block = Block(0, "Intra16x16DCLevel", self)
            for i in range(16):
                self.luma_blocks.append(Block(i, "Intra16x16ACLevel", self))

        self.chroma_dc_blocks = [Block(0, "ChromaDCLevel", self, "Cb"),
                                 Block(1, "ChromaDCLevel", self, "Cr")]
        self.chroma_ac_blocks = [None, None]
        for i in range(2):
            self.chroma_ac_blocks[i] = []
            for j in range(4):
                color = "Cb" if i == 0 else "Cr"
                blk = Block(j, "ChromaACLevel", self, color)
                self.chroma_ac_blocks[i].append(blk)
        # self.luma_i16x16_ac_block = []
        # if "16x16" in self.mb_type:
        #     for i in range(16):
        #         self.luma_i16x16_ac_block.append(Block(i, "Intra16x16ACLevel", self))

    def parse(self):
        print("  MacroBlock ", self.addr, " Decoding...")
        self.init_params()
        self.macroblock_layer()

    def init_params(self):
        self.params["transform_size_8x8_flag"] = 0
        self.params["prev_intra4x4_pred_mode_flag"] = [None]*16
        self.params["prev_intra8x8_pred_mode_flag"] = [None]*16
        self.params["rem_intra4x4_pred_mode"] = [None]*16
        self.params["rem_intra8x8_pred_mode"] = [None]*16

    def macroblock_layer(self) :
        self.mb_pred()
        if self.pred_mode != "Intra_16x16" :
            self.coded_block_pattern = self.slice.bits.me(self.pred_mode, self.slice.sps["ChromaArrayType"])
            self.CodedBlockPatternLuma = self.coded_block_pattern % 16
            self.CodedBlockPatternChroma = self.coded_block_pattern // 16
        if self.CodedBlockPatternLuma > 0 or self.CodedBlockPatternChroma > 0 or \
           self.pred_mode == "Intra_16x16" :
            self.mb_qp_delta = self.slice.bits.se()
            self.residual(0, 15)


    def mb_pred(self):
        if self.pred_mode == "Intra_4x4" or \
           self.pred_mode == "Intra_8x8" or \
           self.pred_mode == "Intra_16x16":
            if self.pred_mode == "Intra_4x4":
                for luma4x4BlkIdx in range(16):
                    self.luma_blocks[luma4x4BlkIdx].prev_intra4x4_pred_mode_flag = self.slice.bits.u(1)
                    if not self.luma_blocks[luma4x4BlkIdx].prev_intra4x4_pred_mode_flag:
                        self.luma_blocks[luma4x4BlkIdx].rem_intra4x4_pred_mode = self.slice.bits.u(3)
            if self.pred_mode == "Intra_8x8":
                raise NameError("I8x8 not Impl")
            if self.slice.sps["ChromaArrayType"] == 1 or self.slice.sps["ChromaArrayType"] == 2:
                self.intra_chroma_pred_mode = self.slice.bits.ue()
        elif self.pred_mode != "Direct":
            raise NameError("pred mode direct not impl")
            # for mbPartIdx in range(NumMbPart(mb_type)):
            #     if self.params["num_ref_idx_l0_active_minus1"] > 0 or \
            #        self.params["mb_field_decoding_flag"] != self.params["field_pic_flag"] and \
            #        self.MbPartPredMode(mb_type, mbPartIdx) != "Pred_L1":
            #         self.params["ref_idx_l0"][mbPartIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.te()
            # for mbPartIdx in range(NumMbPart(mb_type)):
            #     if self.params["num_ref_idx_l1_active_minus1"] > 0 or \
            #        self.params["mb_field_decoding_flag"] != self.params["field_pic_flag"] and \
            #        self.MbPartPredMode(mb_type, mbPartIdx ) != "Pred_L0":
            #         self.params["ref_idx_l1"][mbPartIdx] =self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.te()
            # for mbPartIdx in range(NumMbPart(mb_type)):
            #     if self.MbPartPredMode(mb_type, mbPartIdx ) != "Pred_L1":
            #         for compIdx in range(2):
            #             self.params["mvd_l0"][mbPartIdx][0][compIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.se()
            # for mbPartIdx in range(NumMbPart(mb_type)):
            #     if self.MbPartPredMode(mb_type, mbPartIdx ) != "Pred_L0":
            #         for compIdx in range(2):
            #             self.params["mvd_l1"][mbPartIdx][0][compIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag"] else self.slice.bits.se()

    def residual(self, startIdx, endIdx):
        self.residual_luma(startIdx, endIdx)
        if self.slice.sps["ChromaArrayType"] == 1 or self.slice.sps["ChromaArrayType"] == 2:
            NumC8x8 = 4 // (self.slice.sps["SubWidthC"] * self.slice.sps["SubHeightC"])
            for iCbCr in range(2):
                if self.CodedBlockPatternChroma & 3 and startIdx == 0:
                    self.chroma_dc_blocks[iCbCr].parse(0,4 * NumC8x8 - 1, 4 * NumC8x8)
                else:
                    self.chroma_dc_blocks[iCbCr].ChromaDCLevel = [0] * (4 * NumC8x8)
            for iCbCr in range(2):
                for i8x8 in range(NumC8x8):
                    for i4x4 in range(4):
                        if self.CodedBlockPatternChroma & 2:
                            self.chroma_ac_blocks[iCbCr][i8x8*4+i4x4].parse(max(0, startIdx-1), endIdx-1, 15)
                        else:
                            self.chroma_ac_blocks[iCbCr][i8x8*4+i4x4].ChromaACLevel = [0] * 16
        elif self.slice.sps["ChromaArrayType"] == 3:
            raise NameError("ChromaArrayType == 3 not impl")

    def residual_luma(self, startIdx, endIdx):
        if startIdx == 0 and \
           self.pred_mode == "Intra_16x16":
            self.luma_i16x16_dc_block.parse(0, 15, 16)
        for i8x8 in range(4):
            for i4x4 in range(4):
                if self.CodedBlockPatternLuma & (1 << i8x8):
                    if self.pred_mode == "Intra_16x16":
                        # raise NameError("i16x16 not impl")
                        self.luma_blocks[i8x8 * 4 + i4x4].parse(max(0, startIdx - 1), endIdx - 1, 15)
                        # self.residual_block(self.i16x16AClevel[i8x8 * 4 + i4x4], max(0, startIdx - 1), endIdx - 1, 15, "Intra16x16ACLevel")
                    else:
                        self.luma_blocks[i8x8 * 4 + i4x4].mode = "LumaLevel4x4"
                        self.luma_blocks[i8x8 * 4 + i4x4].parse(startIdx, endIdx, 16)
                elif self.pred_mode == "Intra_16x16":
                    # raise NameError("i16x16 not impl")
                    self.luma_blocks[i8x8 * 4 + i4x4].coeffLevel = [0]*15
                else:
                    self.luma_blocks[i8x8 * 4 + i4x4].coeffLevel = [0] * 16
                if not self.slice.pps["entropy_coding_mode_flag"] and \
                   self.params["transform_size_8x8_flag"]:
                    raise NameError("mb 123")
                    for i in range(16):
                        self.level8x8[ i8x8 ][ 4 * i + i4x4 ] = self.level4x4[ i8x8 * 4 + i4x4 ][ i ]

    def MbPartPredMode(self, mb_type_int, n = 0):
        if mb_type_int == 0:
            return "Intra_4x4"
        elif mb_type_int >= 1 and mb_type_int <= 24:
            self.Intra16x16PredMode = (mb_type_int - 1) % 4
            self.CodedBlockPatternChroma = ((mb_type_int - 1) // 4) % 3
            self.CodedBlockPatternLuma = (mb_type_int // 13) * 15
            return "Intra_16x16"
        else:
            raise NameError("Unknown MbPartPredMode")

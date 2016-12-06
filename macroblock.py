from block import Block
from pprint import pprint
from utilities import array_2d, Clip3

mbtype_islice_table = ["I_NxN","I_16x16_0_0_0","I_16x16_1_0_0","I_16x16_2_0_0","I_16x16_3_0_0","I_16x16_0_1_0","I_16x16_1_1_0","I_16x16_2_1_0","I_16x16_3_1_0","I_16x16_0_2_0","I_16x16_1_2_0","I_16x16_2_2_0","I_16x16_3_2_0","I_16x16_0_0_1","I_16x16_1_0_1","I_16x16_2_0_1","I_16x16_3_0_1","I_16x16_0_1_1","I_16x16_1_1_1","I_16x16_2_1_1","I_16x16_3_1_1","I_16x16_0_2_1","I_16x16_1_2_1","I_16x16_2_2_1","I_16x16_3_2_1","I_PCM"]
mbtype_pslice_table = ["P_L0_16x16", "P_L0_L0_16x8", "P_L0_L0_8x16", "P_8x8", "P_8x8ref0", "P_Skip"]

class Macroblock:

    def __init__(self, parent_slice, idx, pskip = False):
        self.idx = idx
        self.slice = parent_slice
        self.params = {}
        self.var = {}
        if pskip:
            self.mb_type_int = 5
        else:
            self.mb_type_int = self.slice.bits.ue()
        if self.slice.slice_type == "I":
            self.mb_type = mbtype_islice_table[self.mb_type_int]
        elif self.slice.slice_type == "P":
            self.mb_type = mbtype_pslice_table[self.mb_type_int]
        else:
            raise NameError("Unknow MB Type")
        self.pred_mode = self.MbPartPredMode(self.mb_type_int)
        self.luma_blocks = []
        if self.pred_mode == "Intra4x4":
            for i in range(16):
                self.luma_blocks.append(Block(i, self, "Y", "4x4"))
        elif self.pred_mode == "Intra8x8":
            for i in range(4):
                self.luma_blocks.append(Block(i, self, "Y", "8x8"))
        elif self.pred_mode == "Intra16x16":
            self.luma_i16x16_dc_block = Block(0, self, "Y", "16x16", "DC")
            for i in range(16):
                self.luma_blocks.append(Block(i, self, "Y", "16x16", "AC"))

        self.chroma_dc_blocks = [Block(0, self, "Cb", "", "DC"),
                                 Block(1, self, "Cr", "", "DC")]
        self.chroma_ac_blocks = [None, None]
        for i in range(2):
            self.chroma_ac_blocks[i] = []
            for j in range(4):
                color = "Cb" if i == 0 else "Cr"
                blk = Block(j, self, color,None, "AC")
                self.chroma_ac_blocks[i].append(blk)
        # self.luma_i16x16_ac_block = []
        # if "16x16" in self.mb_type:
        #     for i in range(16):
        #         self.luma_i16x16_ac_block.append(Block(i, "Intra16x16ACLevel", self))

    def parse(self):
        # print("  MacroBlock ", self.addr, " Decoding...")
        self.init_params()
        self.macroblock_layer()

    def init_params(self):
        self.transform_size_8x8_flag = 0
        self.prev_intra4x4_pred_mode_flag = [None]*16
        self.prev_intra8x8_pred_mode_flag = [None]*16
        self.rem_intra4x4_pred_mode = [None]*16
        self.rem_intra8x8_pred_mode = [None]*16
        self.pred_L = array_2d(16,16)

    def macroblock_layer(self) :
        self.mb_pred()
        if self.pred_mode != "Intra16x16" :
            self.coded_block_pattern = self.slice.bits.me(self.pred_mode, self.slice.sps.ChromaArrayType)
            self.CodedBlockPatternLuma = self.coded_block_pattern % 16
            self.CodedBlockPatternChroma = self.coded_block_pattern // 16
        if self.CodedBlockPatternLuma > 0 or self.CodedBlockPatternChroma > 0 or \
           self.pred_mode == "Intra16x16" :
            self.mb_qp_delta = self.slice.bits.se()

            if self.idx == 0:
                SliceQP_Y = 26 + self.slice.pps.pic_init_qp_minus26 + self.slice.slice_qp_delta
                QP_YPREV = SliceQP_Y
            else:
                QP_YPREV = self.slice.mbs[self.idx - 1].QP_Y
            QpBdOffset_Y = self.slice.sps.QpBdOffset_Y
            self.QP_Y = ( ( QP_YPREV + self.mb_qp_delta + 52 + 2 * QpBdOffset_Y ) % (52 + QpBdOffset_Y)) - QpBdOffset_Y
            self.QP_prime_Y = self.QP_Y + QpBdOffset_Y
            if self.slice.sps.qpprime_y_zero_transform_bypass_flag == 1 and QP_prime_Y == 0:
                self.TransformBypassModeFlag = 1
            else:
                self.TransformBypassModeFlag = 0

            table_8_15 = [29,30,31,32,32,33,34,34,35,35,36,36,37,37,37,38,38,38,39,39,39,39]
            # Cb
            qP_Offset = self.slice.pps.chroma_qp_index_offset
            qP_I = Clip3(-self.slice.sps.QpBdOffset_C, 51, self.QP_Y + qP_Offset)
            self.QP_C = qP_I if qP_I < 30 else table_8_15[qP_I - 30]
            self.QP_prime_C = self.QP_C + self.slice.sps.QpBdOffset_C

            self.residual(0, 15)


    def mb_pred(self):
        if self.pred_mode == "Intra4x4" or \
           self.pred_mode == "Intra8x8" or \
           self.pred_mode == "Intra16x16":
            if self.pred_mode == "Intra4x4":
                for luma4x4BlkIdx in range(16):
                    self.luma_blocks[luma4x4BlkIdx].prev_intra4x4_pred_mode_flag = self.slice.bits.u(1)
                    if not self.luma_blocks[luma4x4BlkIdx].prev_intra4x4_pred_mode_flag:
                        self.luma_blocks[luma4x4BlkIdx].rem_intra4x4_pred_mode = self.slice.bits.u(3)
                    # print("rev_pred_mode_flag:", self.luma_blocks[luma4x4BlkIdx].prev_intra4x4_pred_mode_flag)
            if self.pred_mode == "Intra8x8":
                raise NameError("I8x8 not Impl")
            if self.slice.sps.ChromaArrayType == 1 or self.slice.sps.ChromaArrayType == 2:
                self.intra_chroma_pred_mode = self.slice.bits.ue()
        elif self.pred_mode != "Direct":
            raise NameError("pred mode direct not impl")
            # for mbPartIdx in range(NumMbPart(mb_type)):
            #     if self.num_ref_idx_l0_active_minus1 > 0 or \
            #        self.mb_field_decoding_flag"] != self.params["field_pic_flag and \
            #        self.MbPartPredMode(mb_type, mbPartIdx) != "Pred_L1":
            #         self.ref_idx_l0"][mbPartIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag else self.slice.bits.te()
            # for mbPartIdx in range(NumMbPart(mb_type)):
            #     if self.num_ref_idx_l1_active_minus1 > 0 or \
            #        self.mb_field_decoding_flag"] != self.params["field_pic_flag and \
            #        self.MbPartPredMode(mb_type, mbPartIdx ) != "Pred_L0":
            #         self.ref_idx_l1"][mbPartIdx] =self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag else self.slice.bits.te()
            # for mbPartIdx in range(NumMbPart(mb_type)):
            #     if self.MbPartPredMode(mb_type, mbPartIdx ) != "Pred_L1":
            #         for compIdx in range(2):
            #             self.mvd_l0"][mbPartIdx][0][compIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag else self.slice.bits.se()
            # for mbPartIdx in range(NumMbPart(mb_type)):
            #     if self.MbPartPredMode(mb_type, mbPartIdx ) != "Pred_L0":
            #         for compIdx in range(2):
            #             self.mvd_l1"][mbPartIdx][0][compIdx] = self.slice.bits.ae() if self.slice.pps["entropy_coding_mode_flag else self.slice.bits.se()

    def residual(self, startIdx, endIdx):
        self.residual_luma(startIdx, endIdx)
        if self.slice.sps.ChromaArrayType == 1 or self.slice.sps.ChromaArrayType == 2:
            NumC8x8 = 4 // (self.slice.sps.SubWidthC * self.slice.sps.SubHeightC)
            for iCbCr in range(2):
                if self.CodedBlockPatternChroma & 3 and startIdx == 0:
                    self.chroma_dc_blocks[iCbCr].parse(0,4 * NumC8x8 - 1, 4 * NumC8x8)
                else:
                    self.chroma_dc_blocks[iCbCr].coeffLevel = [0] * (4 * NumC8x8)
            for iCbCr in range(2):
                for i8x8 in range(NumC8x8):
                    for i4x4 in range(4):
                        if self.CodedBlockPatternChroma & 2:
                            self.chroma_ac_blocks[iCbCr][i8x8*4+i4x4].parse(max(0, startIdx-1), endIdx-1, 15)
                        else:
                            self.chroma_ac_blocks[iCbCr][i8x8*4+i4x4].coeffLevel = [0] * 16
        elif self.slice.sps.ChromaArrayType == 3:
            raise NameError("ChromaArrayType == 3 not impl")

    def residual_luma(self, startIdx, endIdx):
        if startIdx == 0 and \
           self.pred_mode == "Intra16x16":
            self.luma_i16x16_dc_block.parse(0, 15, 16)
        for i8x8 in range(4):
            for i4x4 in range(4):
                if self.CodedBlockPatternLuma & (1 << i8x8):
                    if self.pred_mode == "Intra16x16":
                        # raise NameError("i16x16 not impl")
                        self.luma_blocks[i8x8 * 4 + i4x4].parse(max(0, startIdx - 1), endIdx - 1, 15)
                        # self.residual_block(self.i16x16AClevel[i8x8 * 4 + i4x4], max(0, startIdx - 1), endIdx - 1, 15, "Intra16x16ACLevel")
                    else:
                        self.luma_blocks[i8x8 * 4 + i4x4].color = "Y"
                        self.luma_blocks[i8x8 * 4 + i4x4].size = "4x4"
                        self.luma_blocks[i8x8 * 4 + i4x4].parse(startIdx, endIdx, 16)
                elif self.pred_mode == "Intra16x16":
                    # raise NameError("i16x16 not impl")
                    self.luma_blocks[i8x8 * 4 + i4x4].coeffLevel = [0]*15
                else:
                    self.luma_blocks[i8x8 * 4 + i4x4].coeffLevel = [0] * 16
                if not self.slice.pps.entropy_coding_mode_flag and \
                   self.transform_size_8x8_flag:
                    raise NameError("mb 123")
                    for i in range(16):
                        self.level8x8[ i8x8 ][ 4 * i + i4x4 ] = self.level4x4[ i8x8 * 4 + i4x4 ][ i ]

    def MbPartPredMode(self, mb_type_int, n = 0):
        if mb_type_int == 0:
            return "Intra4x4"
        elif mb_type_int >= 1 and mb_type_int <= 24:
            self.Intra16x16PredMode = (mb_type_int - 1) % 4
            self.CodedBlockPatternChroma = ((mb_type_int - 1) // 4) % 3
            self.CodedBlockPatternLuma = (mb_type_int // 13) * 15
            return "Intra16x16"
        elif (mb_type_int, n) in [(0,0), (1,0), (2,0), (5,0), (1,1), (2,1)]:
            self.NumMbPart = [1,2,2,4,4,1][mb_type_int]
            self.MbPartWidth = [16,16,8,8,8,16][mb_type_int]
            self.MbPartHeight = [16,8,16,8,8,16][mb_type_int]
            return "Pred_L0"
        else:
            raise NameError("Unknown MbPartPredMode")

    def luma_neighbor_location(self, xN, yN):
        # 6.4.12
        maxW = 16
        maxH = 16
        if self.slice.MbaffFrameFlag == 0:
            # 6.4.12.1
            tmp = self.belongMB(xN, yN, maxW, maxH)
            if tmp == "A":
                mbAddrTmp = self.idx - 1
                if mbAddrTmp < 0 or mbAddrTmp > self.idx or self.idx % self.slice.PicWidthInMbs == 0:
                    mbAddrTmp = None
            elif tmp == "B":
                mbAddrTmp = self.idx - self.slice.PicWidthInMbs
                if mbAddrTmp < 0 or mbAddrTmp > self.idx:
                    mbAddrTmp = None
            elif tmp == "X":
                mbAddrTmp = self.idx
            elif tmp == "C":
                mbAddrTmp = self.idx - self.slice.PicWidthInMbs + 1
                if mbAddrTmp < 0 or mbAddrTmp > self.idx or self.idx+1 % self.slice.PicWidthInMbs == 0:
                    mbAddrTmp = None
            elif tmp == "D":
                mbAddrTmp = self.idx - self.slice.PicWidthInMbs - 1
                if mbAddrTmp < 0 or mbAddrTmp > self.idx or self.idx % self.slice.PicWidthInMbs == 0:
                    mbAddrTmp = None
            else:
                mbAddrTmp = None
            xW = ( xN + maxW ) % maxW
            yW = ( yN + maxH ) % maxH
        else:
            # 6.4.12.2
            raise NameError("6.4.12.2 not impl")
        return (mbAddrTmp, xW, yW)

    def chroma_neighbor_location(self, xN, yN):
        maxW = self.slice.sps.MbWidthC
        maxH = self.slice.sps.MbHeightC
        if self.slice.MbaffFrameFlag == 0:
            tmp = self.belongMB(xN, yN, maxW, maxH)
            if tmp == "A":
                mbAddrTmp = self.idx - 1
                if mbAddrTmp < 0 or mbAddrTmp > self.idx or self.idx % self.slice.PicWidthInMbs == 0:
                    mbAddrTmp = None
            elif tmp == "B":
                mbAddrTmp = self.idx - self.slice.PicWidthInMbs
                if mbAddrTmp < 0 or mbAddrTmp > self.idx:
                    mbAddrTmp = None
            elif tmp == "X":
                mbAddrTmp = self.idx
            elif tmp == "C":
                mbAddrTmp = self.idx - self.slice.PicWidthInMbs + 1
                if mbAddrTmp < 0 or mbAddrTmp > self.idx or self.idx+1 % self.slice.PicWidthInMbs == 0:
                    mbAddrTmp = None
            elif tmp == "D":
                mbAddrTmp = self.idx - self.slice.PicWidthInMbs - 1
                if mbAddrTmp < 0 or mbAddrTmp > self.idx or self.idx % self.slice.PicWidthInMbs == 0:
                    mbAddrTmp = None
            else:
                raise NameError("direction impossible")
            xW = ( xN + maxW ) % maxW
            yW = ( yN + maxH ) % maxH
        else:
            # 6.4.12.2
            raise NameError("6.4.12.2 not impl")
        return (mbAddrTmp, xW, yW)

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

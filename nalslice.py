from nalunit import NalUnit
from macroblock import Macroblock
from pprint import pprint
from utilities import array_2d

class Slice:
    slice_types = {0:"P",1:"B",2:"I",3:"SP",4:"SI",5:"P",6:"B",7:"I",8:"SP",9:"SI"}

    def rbsp_trailing_bits(self):
        # if self.bits.more_data():
        self.rbsp_stop_one_bit = self.bits.f(1)
        assert self.rbsp_stop_one_bit == 1
        # self.params["rbsp_alignment_zero_bit"] = self.bits[self.bits.pos:].int
        while not self.bits.byte_aligned():
            assert self.bits.f(1) == 0  

    def __init__(self, bits, sps, ppss, params):
        self.bits = bits
        self.sps = sps
        self.pps_list = ppss
        for k in params:
            self.__dict__[k] = params[k]
        self.var = {}
        self.mbs = []
        self.parse()

    def parse(self):
        self.slice_layer_without_partitioning_rbsp()

    def slice_layer_without_partitioning_rbsp(self):
        self.slice_header()
        # print("\nSLICE HEADER:")
        # pprint(self.params)

        self.slice_variables()
        # print("\nSLICE VAR:")
        # pprint(self.var)

        # print("SLICE DATA:")
        self.slice_data()

    def slice_header(self) :
        self.IdrPicFlag = 1 if self.nal_unit_type == 5 else 0
        self.first_mb_in_slice = self.bits.ue()
        self.slice_type_int = self.bits.ue()
        self.slice_type = NalUnit.slice_types[self.slice_type_int]
        self.pic_parameter_set_id = self.bits.ue()
        self.pps = self.pps_list[self.pic_parameter_set_id]
        if self.sps.separate_colour_plane_flag == 1 :
            self.colour_plane_id = self.bits.u(2)
        self.frame_num = self.bits.u(self.sps.log2_max_frame_num_minus4 + 4)
        if self.sps.frame_mbs_only_flag == 0 :
            self.field_pic_flag = self.bits.u(1)
            if self.field_pic_flag > 0 :
                self.bottom_field_flag = self.bits.u(1)
        else:
            self.field_pic_flag = 0
        if self.IdrPicFlag :
            self.idr_pic_id = self.bits.ue()
        if self.sps.pic_order_cnt_type == 0 :
            self.pic_order_cnt_lsb = \
                self.bits.u(self.sps.log2_max_pic_order_cnt_lsb_minus4 + 4)
            if (self.pps.bottom_field_pic_order_in_frame_present_flag > 0) and \
               (self.field_pic_flag == 0) :
                self.delta_pic_order_cnt_bottom = self.bits.se()
        self.delta_pic_order_cnt = []
        if (self.sps.pic_order_cnt_type == 1) and \
           (self.delta_pic_order_always_zero_flag == 0) :
            self.delta_pic_order_cnt.append(self.bits.se())
            if self.bottom_field_pic_order_in_frame_present_flag and (not self.field_pic_flag) :
                self.delta_pic_order_cnt.append(self.bits.se())
        if self.pps.redundant_pic_cnt_present_flag > 0 :
            self.redundant_pic_cnt = self.bits.ue()
        if self.slice_type == "B" :
            self.direct_spatial_mv_pred_flag = self.bits.u(1)
        if self.slice_type == "P" or self.slice_type == "SP" or self.slice_type == "B" :
            self.num_ref_idx_active_override_flag = self.bits.u(1)
            if self.num_ref_idx_active_override_flag > 0 :
                self.num_ref_idx_l0_active_minus1 = self.bits.ue()
                if self.slice_type == "B" :
                    self.num_ref_idx_l1_active_minus1 = self.bits.ue()
        if self.nal_unit_type == 20 or self.nal_unit_type == 21 :
            self.ref_pic_list_mvc_modification()
        else:
            self.ref_pic_list_modification()
        if (self.pps.weighted_pred_flag > 0) and \
           ((self.slice_type == "P") or (slice_type == "SP")) or \
           ((self.pps.weighted_bipred_idc == 1) and (self.slice_type == "B")) :
            self.pred_weight_table()
        if self.nal_ref_idc != 0 :
            self.dec_ref_pic_marking()
        if self.pps.entropy_coding_mode_flag and \
           (self.slice_type != "I") and \
           (self.slice_type != "SI") :
            self.cabac_init_idc = self.bits.ue()
        self.slice_qp_delta = self.bits.se()
        if (self.slice_type == "SP") or (self.slice_type == "SI") :
            if self.slice_type == "SP" :
                self.sp_for_switch_flag = self.bits.u(1)
            self.slice_qs_delta = self.bits.se()
        if self.pps.deblocking_filter_control_present_flag :
            self.disable_deblocking_filter_idc = self.bits.ue()
            if self.disable_deblocking_filter_idc != 1 :
                self.slice_alpha_c0_offset_div2 = self.bits.se()
                self.slice_beta_offset_div2 = self.bits.se()
        if self.pps.num_slice_groups_minus1 > 0 and \
           self.slice_group_map_type >= 3 and \
           self.slice_group_map_type <= 5:
            #WIP UV
            print("slice_group_change_cycle NOT impl")
            #self.slice_group_change_cycle = self.bits.u()

    def slice_variables(self):
        self.PrevRefFrameNum = 0 if self.nal_unit_type == 5 else 1 # TO BE FIXED
        self.MbaffFrameFlag = self.sps.mb_adaptive_frame_field_flag and \
                                     (not self.field_pic_flag)
        self.PicWidthInMbs = self.sps.pic_width_in_mbs_minus1 + 1
        self.PicWidthInSamples_L = self.PicWidthInMbs * 16
        self.PicWidthInSamples_C = self.PicWidthInMbs * self.sps.MbWidthC
        self.PicHeightInMapUnits = self.sps.pic_height_in_map_units_minus1 + 1
        self.FrameHeightInMbs = ( 2 - self.sps.frame_mbs_only_flag ) * self.PicHeightInMapUnits
        self.PicHeightInMbs = self.FrameHeightInMbs / ( 1 + self.field_pic_flag )
        self.PicSizeInMapUnits = self.PicWidthInMbs * self.PicHeightInMapUnits
        self.PicSizeInMbs = self.PicWidthInMbs * self.PicHeightInMbs
        self.PicHeightInSamples_L = int(self.PicHeightInMbs * 16)
        self.PicHeightInSamples_C = int(self.PicHeightInMbs * self.sps.MbHeightC)
        self.S_prime_L = array_2d(self.PicWidthInSamples_L, self.PicHeightInSamples_L, 0)
        self.S_prime_Cb = array_2d(self.PicWidthInSamples_C, self.PicHeightInSamples_C, 0)
        self.S_prime_Cr = array_2d(self.PicWidthInSamples_C, self.PicHeightInSamples_C, 0)
        self.mb_to_slice_group_map()

    def ref_pic_list_mvc_modification(self):
        print("ref_pic_list_mvc_modification NOT IMPL")

    def ref_pic_list_modification(self):
        if (self.slice_type_int % 5 != 2) and (self.slice_type_int % 5 != 4) :
            self.ref_pic_list_modification_flag_l0 = self.bits.u(1)
            if self.ref_pic_list_modification_flag_l0 :
                while True :
                    self.modification_of_pic_nums_idc = self.bits.ue()
                    if self.modification_of_pic_nums_idc == 0 or \
                       self.modification_of_pic_nums_idc == 1 :
                        self.abs_diff_pic_num_minus1 = self.bits.ue()
                    elif self.modification_of_pic_nums_idc == 2 :
                        self.long_term_pic_num = self.bits.ue()
                    if self.modification_of_pic_nums_idc == 3:
                        break
        if self.slice_type_int % 5 == 1 :
            self.ref_pic_list_modification_flag_l1 = self.bits.u(1)
            if self.ref_pic_list_modification_flag_l1: 
                while True :
                    self.modification_of_pic_nums_idc = self.bits.ue()
                    if (self.modification_of_pic_nums_idc == 0) or \
                       (self.modification_of_pic_nums_idc == 1) :
                        self.abs_diff_pic_num_minus1 = self.bits.ue()
                    elif self.modification_of_pic_nums_idc == 2 :
                        self.long_term_pic_num = self.bits.ue()
                    if self.modification_of_pic_nums_idc == 3 :
                        break


    def pred_weight_table(self):
        print("pred_weight_table NOT impl")
        pass

    def dec_ref_pic_marking(self):
        if self.IdrPicFlag :
            self.no_output_of_prior_pics_flag = self.bits.u(1)
            self.long_term_reference_flag = self.bits.u(1)
        else :
            self.adaptive_ref_pic_marking_mode_flag = self.bits.u(1)
            if self.adaptive_ref_pic_marking_mode_flag :
                while True :
                    memory_management_control_operation = self.bits.ue()
                    self.memory_management_control_operation = memory_management_control_operation
                    if memory_management_control_operation == 1 or \
                       memory_management_control_operation == 3 :
                        self.difference_of_pic_nums_minus1 = self.bits.ue()
                    if memory_management_control_operation == 2 :
                        self.long_term_pic_num = self.bits.ue()
                    if memory_management_control_operation == 3 or \
                       memory_management_control_operation == 6 :
                        self.long_term_frame_idx = self.bits.ue()
                    if memory_management_control_operation == 4 :
                        self.max_long_term_frame_idx_plus1 = self.bits.ue()
                    if memory_management_control_operation == 0 :
                        break

    def NextMbAddress(self,n):
        i=n+1 
        while i < self.PicSizeInMbs and self.MbToSliceGroupMap[i] != self.MbToSliceGroupMap[n] :
            i += 1
        return i

    def mb_to_slice_group_map(self) :
        mapUnitToSliceGroupMap = [None] * 100
        mbToSliceGroupMap = [None] * 100
        if self.pps.num_slice_groups_minus1 == 0:
            for i in range(self.PicSizeInMapUnits):
                mapUnitToSliceGroupMap[i] = 0
        else:
            if self.slice_group_map_type == 0:
                # 8.2.2.1
                i=0
                while True :
                    iGroup = 0
                    while iGroup <= self.num_slice_groups_minus1 and i < self.PicSizeInMapUnits :
                        j = 0
                        while j <= self.run_length_minus1[iGroup] and i+j < self.PicSizeInMapUnits :
                            mapUnitToSliceGroupMap[i+j] = iGroup
                            j += 1
                        i += self.run_length_minus1[iGroup] + 1
                        iGroup += 1
                    if i < self.PicSizeInMapUnits :
                        break
            elif self.slice_group_map_type == 1:
                # 8.2.2.2
                for i in range(self.PicSizeInMapUnits):
                    mapUnitToSliceGroupMap[i] = ( ( i % self.PicWidthInMbs ) + \
                        ( ( ( i / self.PicWidthInMbs ) * ( self.num_slice_groups_minus1 + 1 ) ) / 2 ) ) % \
                    ( self.num_slice_groups_minus1 + 1 )
            elif self.slice_group_map_type == 2:
                # 8.2.2.3
                for i in range(self.PicSizeInMapUnits):
                    mapUnitToSliceGroupMap[i] = self.num_slice_groups_minus1
                iGroup = self.num_slice_groups_minus1 - 1
                while iGroup >= 0:
                    yTopLeft = self.top_left[ iGroup ] / self.PicWidthInMbs 
                    xTopLeft = self.top_left[ iGroup ] % self.PicWidthInMbs 
                    yBottomRight = self.bottom_right[ iGroup ] / self.PicWidthInMbs 
                    xBottomRight = self.bottom_right[ iGroup ] % self.PicWidthInMbs
                    for y in range(yTopLeft, yBottomRight+1):
                        for x in range(xTopLeft, xBottomRight+1):
                            mapUnitToSliceGroupMap[y * self.PicWidthInMbs + x] = iGroup
                    iGroup -= 1
            elif self.slice_group_map_type == 3:
                # 8.2.2.4
                for i in range(self.PicSizeInMapUnits):
                    mapUnitToSliceGroupMap[i] = 1
                x = ( self.PicWidthInMbs - self.slice_group_change_direction_flag ) / 2
                y = ( self.PicHeightInMapUnits - self.slice_group_change_direction_flag ) / 2
                ( leftBound, topBound ) = ( x, y )
                ( rightBound, bottomBound ) = ( x, y )
                ( xDir, yDir ) = ( self.slice_group_change_direction_flag - 1, self.slice_group_change_direction_flag )
                k = 0
                while k < self.MapUnitsInSliceGroup0 :
                    mapUnitVacant = ( mapUnitToSliceGroupMap[ y * self.PicWidthInMbs + x ] == 1 ) 
                    if mapUnitVacant :
                        mapUnitToSliceGroupMap[ y * self.PicWidthInMbs + x ] = 0 
                    if xDir == -1 and x == leftBound :
                        leftBound = max( leftBound - 1, 0 ) 
                        x = leftBound 
                        ( xDir, yDir ) = ( 0, 2 * self.slice_group_change_direction_flag - 1 )
                    elif xDir == 1 and x == rightBound :
                        rightBound = min( rightBound + 1, self.PicWidthInMbs - 1 )
                        x = rightBound
                        ( xDir, yDir ) = ( 0, 1 - 2 * self.slice_group_change_direction_flag ) 
                    elif yDir == -1 and y == topBound :
                        topBound = max( topBound - 1, 0 )
                        y = topBound 
                        ( xDir, yDir ) = ( 1 - 2 * self.slice_group_change_direction_flag, 0 ) 
                    elif yDir == 1 and y == bottomBound : 
                        bottomBound = min( bottomBound + 1, self.PicHeightInMapUnits - 1 ) 
                        y = bottomBound 
                        ( xDir, yDir ) = ( 2 * self.slice_group_change_direction_flag - 1, 0 ) 
                    else :
                        ( x, y ) = ( x + xDir, y + yDir )
            elif self.slice_group_map_type == 4:
                # 8.2.2.5
                for i in range(self.PicSizeInMapUnits):
                    if i < sizeOfUpperLeftGroup :
                        mapUnitToSliceGroupMap[i] = self.slice_group_change_direction_flag
                    else :
                        mapUnitToSliceGroupMap[i] = 1 - self.slice_group_change_direction_flag
            elif self.slice_group_map_type == 5:
                # 8.2.2.6
                k = 0
                for j in range(self.PicWidthInMbs) :
                    for i in range(self.PicHeightInMapUnits) :
                        if k < sizeOfUpperLeftGroup :
                            mapUnitToSliceGroupMap[i * self.PicWidthInMbs + j] = self.slice_group_change_direction_flag
                        else :
                            mapUnitToSliceGroupMap[i * self.PicWidthInMbs + j] = 1 - self.slice_group_change_direction_flag
                        k += 1
            elif self.slice_group_map_type == 6:
                # 8.2.2.7
                mapUnitToSliceGroupMap[i] = self.slice_group_id[i]
        # 8.2.2.8 mapUnitToSliceGroupMap -> mbToSliceGroupMap
        for i in range(int(self.PicSizeInMbs)) :
            if self.sps.frame_mbs_only_flag == 1 or self.field_pic_flag == 1 :
                mbToSliceGroupMap[i] = mapUnitToSliceGroupMap[ i ]
            elif self.MbaffFrameFlag == 1 :
                mbToSliceGroupMap[i] = mapUnitToSliceGroupMap[ i / 2 ]
            elif self.frame_mbs_only_flag == 0 and mb_adaptive_frame_field_flag == 0 and self.field_pic_flag == 0:
                mbToSliceGroupMap[i] = mapUnitToSliceGroupMap[ ( i / ( 2 * self.PicWidthInMbs ) ) * self.PicWidthInMbs + ( i % self.PicWidthInMbs ) ]
        self.MbToSliceGroupMap = list(filter(lambda x: x != None, mbToSliceGroupMap))

    def slice_data(self):
        if self.pps.entropy_coding_mode_flag :
            while self.bits.byte_aligned():
                self.cabac_alignment_one_bit = self.bits.f(1)
        self.CurrMbAddr = self.first_mb_in_slice * ( 1 + self.MbaffFrameFlag )
        moreDataFlag = True
        prevMbSkipped = False
        while True:
            if self.slice_type != "I" and self.slice_type != "SI" :
                if not self.pps.entropy_coding_mode_flag :
                    self.mb_skip_run = self.bits.ue()
                    prevMbSkipped = self.mb_skip_run > 0 
                    for i in range(self.mb_skip_run) :
                        self.CurrMbAddr = self.NextMbAddress( self.CurrMbAddr )
                    if self.mb_skip_run > 0 :
                        moreDataFlag = self.bits.more_rbsp_data( )
                else :
                    self.mb_skip_flag = self.bits.ae()
                    moreDataFlag = not self.mb_skip_flag
            if moreDataFlag :
                if self.MbaffFrameFlag and ( self.CurrMbAddr % 2 == 0 or ( self.CurrMbAddr % 2 == 1 and prevMbSkipped ) ) :
                    self.mb_field_decoding_flag = self.bits.ae() if self.pps.entropy_coding_mode_flag else self.bits.u(1)
                mb = Macroblock(self, len(self.mbs))
                self.mbs.append(mb)
                self.mbs[-1].parse()
            if not self.pps.entropy_coding_mode_flag :
                moreDataFlag = self.bits.more_rbsp_data()
            else :
                if self.slice_type != "I" and self.slice_type != "SI" :
                    prevMbSkipped = self.mb_skip_flag
                if self.MbaffFrameFlag and self.CurrMbAddr % 2 == 0 :
                    moreDataFlag = True
                else :
                    self.end_of_slice_flag = self.bits.ae()
                    moreDataFlag = not self.end_of_slice_flag
            self.CurrMbAddr = self.NextMbAddress(self.CurrMbAddr)
            if not moreDataFlag:
                break


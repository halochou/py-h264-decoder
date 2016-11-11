from nalunit import NalUnit
from macroblock import Macroblock
from pprint import pprint

class Slice(NalUnit):
    slice_types = {0:"P",1:"B",2:"I",3:"SP",4:"SI",5:"P",6:"B",7:"I",8:"SP",9:"SI"}

    def __init__(self, bits, sps, pps, params):
        self.bits = bits
        self.sps = sps.params
        self.pps_list = pps
        self.params = params
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

        print("SLICE DATA:")
        self.slice_data()

    def slice_header(self) :
        self.var["IdrPicFlag"] = 1 if self.params["nal_unit_type"] == 5 else 0
        self.params["first_mb_in_slice"] = self.bits.ue()
        self.params["slice_type_int"] = self.bits.ue()
        self.params["slice_type"] = NalUnit.slice_types[self.params["slice_type_int"]]
        self.params["pic_parameter_set_id"] = self.bits.ue()
        self.pps = self.pps_list[self.params["pic_parameter_set_id"]].params
        if self.sps["separate_colour_plane_flag"] == 1 :
            self.params["colour_plane_id"] = self.bits.u(2)
        self.params["frame_num"] = self.bits.u(self.sps["log2_max_frame_num_minus4"] + 4)
        if self.sps["frame_mbs_only_flag"] == 0 :
            self.params["field_pic_flag"] = self.bits.u(1)
            if self.params["field_pic_flag"] > 0 :
                self.params["bottom_field_flag"] = self.bits.u(1)
        else:
            self.params["field_pic_flag"] = 0
        if self.var["IdrPicFlag"] :
            self.params["idr_pic_id"] = self.bits.ue()
        if self.sps["pic_order_cnt_type"] == 0 :
            self.params["pic_order_cnt_lsb"] = \
                self.bits.u(self.sps["log2_max_pic_order_cnt_lsb_minus4"] + 4)
            if (self.pps["bottom_field_pic_order_in_frame_present_flag"] > 0) and \
               (self.params["field_pic_flag"] == 0) :
                self.params["delta_pic_order_cnt_bottom"] = self.bits.se()
        self.params["delta_pic_order_cnt"] = []
        if (self.sps["pic_order_cnt_type"] == 1) and \
           (self.params["delta_pic_order_always_zero_flag"] == 0) :
            self.params["delta_pic_order_cnt"].append(self.bits.se())
            if self.params["bottom_field_pic_order_in_frame_present_flag"] and (not self.params["field_pic_flag"]) :
                self.params["delta_pic_order_cnt"].append(self.bits.se())
        if self.pps["redundant_pic_cnt_present_flag"] > 0 :
            self.params["redundant_pic_cnt"] = self.bits.ue()
        if self.params["slice_type"] == "B" :
            self.params["direct_spatial_mv_pred_flag"] = self.bits.u(1)
        if self.params["slice_type"] == "P" or self.params["slice_type"] == "SP" or self.params["slice_type"] == "B" :
            self.params["num_ref_idx_active_override_flag"] = self.bits.u(1)
            if self.params["num_ref_idx_active_override_flag"] > 0 :
                self.params["num_ref_idx_l0_active_minus1"] = self.bits.ue()
                if self.params["slice_type"] == "B" :
                    self.params["num_ref_idx_l1_active_minus1"] = self.bits.ue()
        if self.params["nal_unit_type"] == 20 or self.params["nal_unit_type"] == 21 :
            self.ref_pic_list_mvc_modification()
        else:
            self.ref_pic_list_modification()
        if (self.pps["weighted_pred_flag"] > 0) and \
           ((self.params["slice_type"] == "P") or (slice_type == "SP")) or \
           ((self.pps["weighted_bipred_idc"] == 1) and (self.params["slice_type"] == "B")) :
            self.pred_weight_table()
        if self.params["nal_ref_idc"] != 0 :
            self.dec_ref_pic_marking()
        if self.pps["entropy_coding_mode_flag"] and \
           (self.params["slice_type"] != "I") and \
           (self.params["slice_type"] != "SI") :
            self.params["cabac_init_idc"] = self.bits.ue()
        self.params["slice_qp_delta"] = self.bits.se()
        if (self.params["slice_type"] == "SP") or (self.params["slice_type"] == "SI") :
            if self.params["slice_type"] == "SP" :
                self.params["sp_for_switch_flag"] = self.bits.u(1)
            self.params["slice_qs_delta"] = self.bits.se()
        if self.pps["deblocking_filter_control_present_flag"] :
            self.params["disable_deblocking_filter_idc"] = self.bits.ue()
            if self.params["disable_deblocking_filter_idc"] != 1 :
                self.params["slice_alpha_c0_offset_div2"] = self.bits.se()
                self.params["slice_beta_offset_div2"] = self.bits.se()
        if self.pps["num_slice_groups_minus1"] > 0 and \
           self.params["slice_group_map_type"] >= 3 and \
           self.params["slice_group_map_type"] <= 5:
            #WIP UV
            print("slice_group_change_cycle NOT impl")
            #self.params["slice_group_change_cycle"] = self.bits.u()

    def slice_variables(self):
        self.var["PrevRefFrameNum"] = 0 if self.params["nal_unit_type"] == 5 else 1 # TO BE FIXED
        self.var["MbaffFrameFlag"] = self.sps["mb_adaptive_frame_field_flag"] and \
                                     (not self.params["field_pic_flag"])
        self.var["PicWidthInMbs"] = self.sps["pic_width_in_mbs_minus1"] + 1
        self.var["PicHeightInMapUnits"] = self.sps["pic_height_in_map_units_minus1"] + 1
        self.var["FrameHeightInMbs"] = ( 2 - self.sps["frame_mbs_only_flag"] ) * self.var["PicHeightInMapUnits"]
        self.var["PicHeightInMbs"] = self.var["FrameHeightInMbs"] / ( 1 + self.params["field_pic_flag"] )
        self.var["PicSizeInMapUnits"] = self.var["PicWidthInMbs"] * self.var["PicHeightInMapUnits"]
        self.var["PicSizeInMbs"] = self.var["PicWidthInMbs"] * self.var["PicHeightInMbs"]
        self.var["PicHeightInSamplesL"] = self.var["PicHeightInMbs"] * 16
        self.mb_to_slice_group_map()
        # self.var["PicHeightInSamplesC"] = self.var["PicHeightInMbs"] * MbHeightC
        
    def ref_pic_list_mvc_modification(self):
        print("ref_pic_list_mvc_modification NOT IMPL")

    def ref_pic_list_modification(self):
        if (self.params["slice_type_int"] % 5 != 2) and (self.params["slice_type_int"] % 5 != 4) :
            self.params["ref_pic_list_modification_flag_l0"] = self.bits.u(1)
            if self.params["ref_pic_list_modification_flag_l0"] :
                while True :
                    self.params["modification_of_pic_nums_idc"] = self.bits.ue()
                    if self.params["modification_of_pic_nums_idc"] == 0 or \
                       self.params["modification_of_pic_nums_idc"] == 1 :
                        self.params["abs_diff_pic_num_minus1"] = self.bits.ue()
                    elif self.params["modification_of_pic_nums_idc"] == 2 :
                        self.params["long_term_pic_num"] = self.bits.ue()
                    if self.params["modification_of_pic_nums_idc"] == 3:
                        break
        if self.params["slice_type_int"] % 5 == 1 :
            self.params["ref_pic_list_modification_flag_l1"] = self.bits.u(1)
            if self.params["ref_pic_list_modification_flag_l1"]: 
                while True :
                    self.params["modification_of_pic_nums_idc"] = self.bits.ue()
                    if (self.params["modification_of_pic_nums_idc"] == 0) or \
                       (self.params["modification_of_pic_nums_idc"] == 1) :
                        self.params["abs_diff_pic_num_minus1"] = self.bits.ue()
                    elif self.params["modification_of_pic_nums_idc"] == 2 :
                        self.params["long_term_pic_num"] = self.bits.ue()
                    if self.params["modification_of_pic_nums_idc"] == 3 :
                        break


    def pred_weight_table(self):
        print("pred_weight_table NOT impl")
        pass

    def dec_ref_pic_marking(self):
        if self.var["IdrPicFlag"] :
            self.params["no_output_of_prior_pics_flag"] = self.bits.u(1)
            self.params["long_term_reference_flag"] = self.bits.u(1)
        else :
            self.params["adaptive_ref_pic_marking_mode_flag"] = self.bits.u(1)
            if self.params["adaptive_ref_pic_marking_mode_flag"] :
                while True :
                    memory_management_control_operation = self.bits.ue()
                    self.params["memory_management_control_operation"] = memory_management_control_operation
                    if memory_management_control_operation == 1 or \
                       memory_management_control_operation == 3 :
                        self.params["difference_of_pic_nums_minus1"] = self.bits.ue()
                    if memory_management_control_operation == 2 :
                        self.params["long_term_pic_num"] = self.bits.ue()
                    if memory_management_control_operation == 3 or \
                       memory_management_control_operation == 6 :
                        self.params["long_term_frame_idx"] = self.bits.ue()
                    if memory_management_control_operation == 4 :
                        self.params["max_long_term_frame_idx_plus1"] = self.bits.ue()
                    if memory_management_control_operation == 0 :
                        break

    def NextMbAddress(self,n):
        i=n+1 
        while i < self.var["PicSizeInMbs"] and self.var["MbToSliceGroupMap"][i] != self.var["MbToSliceGroupMap"][n] :
            i += 1
        return i

    def mb_to_slice_group_map(self) :
        mapUnitToSliceGroupMap = [None] * 100
        mbToSliceGroupMap = [None] * 100
        if self.pps["num_slice_groups_minus1"] == 0:
            for i in range(self.var["PicSizeInMapUnits"]):
                mapUnitToSliceGroupMap[i] = 0
        else:
            if self.params["slice_group_map_type"] == 0:
                # 8.2.2.1
                i=0
                while True :
                    iGroup = 0
                    while iGroup <= self.params["num_slice_groups_minus1"] and i < self.var["PicSizeInMapUnits"] :
                        j = 0
                        while j <= self.params["run_length_minus1"][iGroup] and i+j < self.var["PicSizeInMapUnits"] :
                            mapUnitToSliceGroupMap[i+j] = iGroup
                            j += 1
                        i += self.params["run_length_minus1"][iGroup] + 1
                        iGroup += 1
                    if i < self.var["PicSizeInMapUnits"] :
                        break
            elif self.params["slice_group_map_type"] == 1:
                # 8.2.2.2
                for i in range(self.var["PicSizeInMapUnits"]):
                    mapUnitToSliceGroupMap[i] = ( ( i % self.var["PicWidthInMbs"] ) + \
                        ( ( ( i / self.var["PicWidthInMbs"] ) * ( self.params["num_slice_groups_minus1"] + 1 ) ) / 2 ) ) % \
                    ( self.params["num_slice_groups_minus1"] + 1 )
            elif self.params["slice_group_map_type"] == 2:
                # 8.2.2.3
                for i in range(self.var["PicSizeInMapUnits"]):
                    mapUnitToSliceGroupMap[i] = self.params["num_slice_groups_minus1"]
                iGroup = self.params["num_slice_groups_minus1"] - 1
                while iGroup >= 0:
                    yTopLeft = self.params["top_left"][ iGroup ] / self.var["PicWidthInMbs"] 
                    xTopLeft = self.params["top_left"][ iGroup ] % self.var["PicWidthInMbs"] 
                    yBottomRight = self.params["bottom_right"][ iGroup ] / self.var["PicWidthInMbs"] 
                    xBottomRight = self.params["bottom_right"][ iGroup ] % self.var["PicWidthInMbs"]
                    for y in range(yTopLeft, yBottomRight+1):
                        for x in range(xTopLeft, xBottomRight+1):
                            mapUnitToSliceGroupMap[y * self.var["PicWidthInMbs"] + x] = iGroup
                    iGroup -= 1
            elif self.params["slice_group_map_type"] == 3:
                # 8.2.2.4
                for i in range(self.var["PicSizeInMapUnits"]):
                    mapUnitToSliceGroupMap[i] = 1
                x = ( self.var["PicWidthInMbs"] - self.params["slice_group_change_direction_flag"] ) / 2
                y = ( self.var["PicHeightInMapUnits"] - self.params["slice_group_change_direction_flag"] ) / 2
                ( leftBound, topBound ) = ( x, y )
                ( rightBound, bottomBound ) = ( x, y )
                ( xDir, yDir ) = ( self.params["slice_group_change_direction_flag"] - 1, self.params["slice_group_change_direction_flag"] )
                k = 0
                while k < self.var["MapUnitsInSliceGroup0"] :
                    mapUnitVacant = ( mapUnitToSliceGroupMap[ y * self.var["PicWidthInMbs"] + x ] == 1 ) 
                    if mapUnitVacant :
                        mapUnitToSliceGroupMap[ y * self.var["PicWidthInMbs"] + x ] = 0 
                    if xDir == -1 and x == leftBound :
                        leftBound = max( leftBound - 1, 0 ) 
                        x = leftBound 
                        ( xDir, yDir ) = ( 0, 2 * self.params["slice_group_change_direction_flag"] - 1 )
                    elif xDir == 1 and x == rightBound :
                        rightBound = min( rightBound + 1, self.var["PicWidthInMbs"] - 1 )
                        x = rightBound
                        ( xDir, yDir ) = ( 0, 1 - 2 * self.params["slice_group_change_direction_flag"] ) 
                    elif yDir == -1 and y == topBound :
                        topBound = max( topBound - 1, 0 )
                        y = topBound 
                        ( xDir, yDir ) = ( 1 - 2 * self.params["slice_group_change_direction_flag"], 0 ) 
                    elif yDir == 1 and y == bottomBound : 
                        bottomBound = min( bottomBound + 1, self.var["PicHeightInMapUnits"] - 1 ) 
                        y = bottomBound 
                        ( xDir, yDir ) = ( 2 * self.params["slice_group_change_direction_flag"] - 1, 0 ) 
                    else :
                        ( x, y ) = ( x + xDir, y + yDir )
            elif self.params["slice_group_map_type"] == 4:
                # 8.2.2.5
                for i in range(self.var["PicSizeInMapUnits"]):
                    if i < sizeOfUpperLeftGroup :
                        mapUnitToSliceGroupMap[i] = self.params["slice_group_change_direction_flag"]
                    else :
                        mapUnitToSliceGroupMap[i] = 1 - self.params["slice_group_change_direction_flag"]
            elif self.params["slice_group_map_type"] == 5:
                # 8.2.2.6
                k = 0
                for j in range(self.var["PicWidthInMbs"]) :
                    for i in range(self.var["PicHeightInMapUnits"]) :
                        if k < sizeOfUpperLeftGroup :
                            mapUnitToSliceGroupMap[i * self.var["PicWidthInMbs"] + j] = self.params["slice_group_change_direction_flag"]
                        else :
                            mapUnitToSliceGroupMap[i * self.var["PicWidthInMbs"] + j] = 1 - self.params["slice_group_change_direction_flag"]
                        k += 1
            elif self.params["slice_group_map_type"] == 6:
                # 8.2.2.7
                mapUnitToSliceGroupMap[i] = self.params["slice_group_id"][i]
        # 8.2.2.8 mapUnitToSliceGroupMap -> mbToSliceGroupMap
        for i in range(int(self.var["PicSizeInMbs"])) :
            if self.sps["frame_mbs_only_flag"] == 1 or self.params["field_pic_flag"] == 1 :
                mbToSliceGroupMap[i] = mapUnitToSliceGroupMap[ i ]
            elif self.var["MbaffFrameFlag"] == 1 :
                mbToSliceGroupMap[i] = mapUnitToSliceGroupMap[ i / 2 ]
            elif self.params["frame_mbs_only_flag"] == 0 and mb_adaptive_frame_field_flag == 0 and self.params["field_pic_flag"] == 0:
                mbToSliceGroupMap[i] = mapUnitToSliceGroupMap[ ( i / ( 2 * self.var["PicWidthInMbs"] ) ) * self.var["PicWidthInMbs"] + ( i % self.var["PicWidthInMbs"] ) ]
        self.var["MbToSliceGroupMap"] = list(filter(lambda x: x != None, mbToSliceGroupMap))

    def slice_data(self):
        if self.pps["entropy_coding_mode_flag"] :
            while self.bits.byte_aligned():
                self.params["cabac_alignment_one_bit"] = self.bits.f(1)
        CurrMbAddr = self.params["first_mb_in_slice"] * ( 1 + self.var["MbaffFrameFlag"] )
        moreDataFlag = True
        prevMbSkipped = False
        while True:
            if self.params["slice_type"] != "I" and self.params["slice_type"] != "SI" :
                if not self.params["entropy_coding_mode_flag"] :
                    self.params["mb_skip_run"] = self.bits.ue()
                    prevMbSkipped = self.params["mb_skip_run"] > 0 
                    for i in range(self.params["mb_skip_run"]) :
                        CurrMbAddr = NextMbAddress( CurrMbAddr )
                    if self.params["mb_skip_run"] > 0 :
                        moreDataFlag = self.more_rbsp_data( )
                else :
                    self.params["mb_skip_flag"] = self.bits.ae()
                    moreDataFlag = not self.params["mb_skip_flag"]
            if moreDataFlag :
                if self.var["MbaffFrameFlag"] and ( CurrMbAddr % 2 == 0 or ( CurrMbAddr % 2 == 1 and prevMbSkipped ) ) :
                    self.params["mb_field_decoding_flag"] = self.bits.ae() if self.pps["entropy_coding_mode_flag"] else self.bits.u(1)
                self.mbs.append(Macroblock(self))
            if not self.pps["entropy_coding_mode_flag"] :
                moreDataFlag = self.bits.more_rbsp_data()
            else :
                if self.params["slice_type"] != "I" and self.params["slice_type"] != "SI" :
                    prevMbSkipped = self.params["mb_skip_flag"]
                if self.var["MbaffFrameFlag"] and CurrMbAddr % 2 == 0 :
                    moreDataFlag = True
                else :
                    self.params["end_of_slice_flag"] = self.bits.ae()
                    moreDataFlag = not self.params["end_of_slice_flag"]
            CurrMbAddr = self.NextMbAddress( CurrMbAddr )
            if not moreDataFlag:
                break


from bitstring import BitStream
from pprint import pprint

class NalUnit:

    slice_types = {0:"P",1:"B",2:"I",3:"SP",4:"SI",5:"P",6:"B",7:"I",8:"SP",9:"SI"}

    def __init__(self, bits, sps = {}, pps = []):
        self.bits = bits[32:]
        self.params = {}
        self.var = {}
        self.sps = sps
        self.pps = pps
        self.parse()

    def u(self,n):
        return self.bits.read(n).uint

    def f(self,n):
        return self.u(n)

    def exp_golomb(self):
        zeros = 0
        while self.bits.read(1).uint == 0:
            zeros += 1
        #pprint("GLOMB", zeros, self.bits.bin, self.bits.pos)
        return 0 if zeros == 0 else 2**zeros - 1 + self.bits.read(zeros).uint
        #return 2**zeros - 1 + self.bits.read(zeros).int

    def ue(self):
        return self.exp_golomb()

    def se(self):
        from math import ceil
        k = self.exp_golomb()
        return (-1)**(k+1) * ceil(k/2)

    def parse(self):
        self.params["forbidden_zero_bit"] = self.f(1)
        self.params["nal_ref_idc"] = self.u(2)
        self.params["nal_unit_type"] = self.u(5)
        # if nal_unit_type == 14 or nal_unit_type == 20 or nal_unit_type == 21 :
        #     if nal_unit_type != 21 :
        #         self.params["svc_extension_flag"] = u(1)
        #     else:
        #         self.params["avc_3d_extension_flag"] = u(1)
        #     if self.params["svc_extension_flag"] :
        #         pass
        if self.params["nal_unit_type"] == 1:
            self.slice_layer_without_partitioning_rbsp()
        elif self.params["nal_unit_type"] == 5:
            self.slice_layer_without_partitioning_rbsp()
        elif self.params["nal_unit_type"] == 7:
            self.seq_parameter_set_rbsp()
        elif self.params["nal_unit_type"] == 8:
            self.pic_parameter_set_rbsp()
        else:
            print("NO MATCH")

    def rbsp_trailing_bits(self):
        self.params["rbsp_stop_one_bit"] = self.f(1)
        assert self.params["rbsp_stop_one_bit"] == 1
        self.params["rbsp_alignment_zero_bit"] = self.bits[self.bits.pos:].int
        assert self.params["rbsp_alignment_zero_bit"] == 0  


    def seq_parameter_set_rbsp(self):
        self.params["profile_idc"] = self.u(8)
        self.params["constraint_set0_flag"] = self.u(1)
        self.params["constraint_set1_flag"] = self.u(1)
        self.params["constraint_set2_flag"] = self.u(1)
        self.params["constraint_set3_flag"] = self.u(1)
        self.params["constraint_set4_flag"] = self.u(1)
        self.params["constraint_set5_flag"] = self.u(1)
        self.params["reserved_zero_2bits"]  = self.u(2)
        self.params["level_idc"] = self.u(8)
        self.params["seq_parameter_set_id"] =  self.ue()
        if self.params["profile_idc"] == 100 or self.params["profile_idc"] == 110 or self.params["profile_idc"] == 122 or self.params["profile_idc"] == 244 or self.params["profile_idc"] == 44 or self.params["profile_idc"] == 83 or self.params["profile_idc"] == 86 or self.params["profile_idc"] == 118 or self.params["profile_idc"] == 128 or self.params["profile_idc"] == 138 or self.params["profile_idc"] == 139 or self.params["profile_idc"] == 134 or self.params["profile_idc"] == 135 :
            self.params["chroma_format_idc"] = self.ue()
            if self.params["chroma_format_idc"] == 3 :
                self.params["separate_colour_plane_flag"] = self.u(1)
            else :
                self.params["separate_colour_plane_flag"] = 0
            self.params["bit_depth_luma_minus8"] = self.ue()
            self.params["bit_depth_chroma_minus8"] = self.ue()
            self.params["qpprime_y_zero_transform_bypass_flag"] = self.u(1)
            self.params["seq_scaling_matrix_present_flag"] = self.u(1)
            #if( seq_scaling_matrix_present_flag )    self.u(1)
            #for( i = 0; i < ( ( chroma_format_idc != 3 ) ? 8 : 12 ); i++ ) {
            #seq_scaling_list_present_flag[ i ]    self.u(1)
            #if( seq_scaling_list_present_flag[ i ] )
            #if( i < 6 )
            #scaling_list( ScalingList4x4[ i ], 16, UseDefaultScalingMatrix4x4Flag[ i ] )
            #else
            #scaling_list( ScalingList8x8[ i − 6 ], 64, UseDefaultScalingMatrix8x8Flag[ i − 6 ] )
        self.params["log2_max_frame_num_minus4"] = self.ue()
        self.params["pic_order_cnt_type"] = self.ue()
        if self.params["pic_order_cnt_type"] == 0 :
            self.params["log2_max_pic_order_cnt_lsb_minus4"] = self.ue()
        # elif self.params["pic_order_cnt_type == 1"] :
        #     self.params["delta_pic_order_always_zero_flag"] = self.u(1)
        #     self.params["offset_for_non_ref_pic"] = self.se()
        #     self.params["offset_for_top_to_bottom_field"] = self.se()
        #     self.params["num_ref_frames_in_pic_order_cnt_cycle"] = self.ue()
        #     for( i = 0; i < num_ref_frames_in_pic_order_cnt_cycle; i++ )
        #         offset_for_ref_frame[ i ] = self.se()
        self.params["max_num_ref_frames"] = self.ue()
        self.params["gaps_in_frame_num_value_allowed_flag"] = self.u(1)
        self.params["pic_width_in_mbs_minus1"] = self.ue()
        self.params["pic_height_in_map_units_minus1"] = self.ue()
        self.params["frame_mbs_only_flag"] = self.u(1)
        if self.params["frame_mbs_only_flag"] == 0 :
            self.params["mb_adaptive_frame_field_flag"] = self.u(1)
        else:
            self.params["mb_adaptive_frame_field_flag"] = 0
        self.params["direct_8x8_inference_flag"] = self.u(1)
        self.params["frame_cropping_flag"] = self.u(1)
        if self.params["frame_cropping_flag"] != 0 :
            self.params["frame_crop_left_offset"] = self.ue()
            self.params["frame_crop_right_offset"] = self.ue()
            self.params["frame_crop_top_offset"] = self.ue()
            self.params["frame_crop_bottom_offset"] = self.ue()
        self.params["vui_parameters_present_flag"] = self.u(1)
        # if self.params["vui_parameters_present_flag"] :
        #     vui_parameters()
        self.rbsp_trailing_bits()
        print("SPS:")
        pprint(self.params)

    def pic_parameter_set_rbsp(self):
        self.params["pic_parameter_set_id"] = self.ue()
        self.params["seq_parameter_set_id"] = self.ue()
        self.params["entropy_coding_mode_flag"] = self.u(1)
        self.params["bottom_field_pic_order_in_frame_present_flag"] = self.u(1)
        self.params["num_slice_groups_minus1"] = self.ue()
        if self.params["num_slice_groups_minus1"] > 0 :
            self.params["slice_group_map_type"] = self.ue()
            if self.params["slice_group_map_type"] == 0 :
                self.params["run_length_minus1"] = []
                for i in range(self.params["num_slice_groups_minus1"]+1):
                    self.params["run_length_minus1"].append(self.ue())
            elif self.params["slice_group_map_type"] == 2 :
                self.params["top_left"] = []
                self.params["bottom_right"] = []
                for i in range(self.params["num_slice_groups_minus1"]):
                    self.params["top_left"].append(self.ue())
                    self.params["bottom_right"].append(self.ue())
            elif self.params["slice_group_map_type"] == 3 or \
                 self.params["slice_group_map_type"] == 4 or \
                 self.params["slice_group_map_type"] == 5 :
                self.params["slice_group_change_direction_flag"] = self.u(1)
                self.params["slice_group_change_rate_minus1"] = self.ue()
            elif self.params["slice_group_map_type"] == 6 :
                self.params["pic_size_in_map_units_minus1"] = self.ue()
                self.params["slice_group_id"] = []
                from math import ceil, log2
                for i in range(self.params["pic_size_in_map_units_minus1"]+1):
                    tmp = self.u(ceil(log2(self.params["num_slice_groups_minus1"]+1)))
                    self.params["slice_group_id"].append(tmp)
        self.params["num_ref_idx_l0_default_active_minus1"] = self.ue()
        self.params["num_ref_idx_l1_default_active_minus1"] = self.ue()
        self.params["weighted_pred_flag"] = self.u(1)
        self.params["weighted_bipred_idc"] = self.u(2)
        self.params["pic_init_qp_minus26"] = self.se()
        self.params["pic_init_qs_minus26"] = self.se()
        self.params["chroma_qp_index_offset"] = self.se()
        self.params["deblocking_filter_control_present_flag"] = self.u(1)
        self.params["constrained_intra_pred_flag"] = self.u(1)
        self.params["redundant_pic_cnt_present_flag"] = self.u(1)
        if self.bits.pos < self.bits.length :
            self.params["transform_8x8_mode_flag"] = self.u(1)
            self.params["pic_scaling_matrix_present_flag"] = self.u(1)
            if self.params["pic_scaling_matrix_present_flag"] > 0 :
                upper = (2 if self.params["chroma_format_idc"] != 3 else 6) * self.params["transform_8x8_mode_flag"]
                self.params["pic_scaling_list_present_flag"] = []
                for i in range(upper) :
                    elem = self.u(1)
                    self.params["pic_scaling_list_present_flag"].append(elem)
                    if elem > 0:
                        if i < 6 :
                            pass
                            #scaling_list( ScalingList4x4[ i ], 16, UseDefaultScalingMatrix4x4Flag[ i ] )
                        else:
                            pass
                            #scaling_list( ScalingList8x8[ i − 6 ], 64, UseDefaultScalingMatrix8x8Flag[ i − 6 ] )
            self.params["second_chroma_qp_index_offset"] = self.se()
        self.rbsp_trailing_bits()
        print("PPS:")
        pprint(self.params)

    def slice_layer_without_partitioning_rbsp(self):
        self.slice_header()
        self.slice_data()

    def slice_header(self) :
        self.var["IdrPicFlag"] = 1 if self.params["nal_unit_type"] == 5 else 0
        self.params["first_mb_in_slice"] = self.ue()
        self.params["slice_type_int"] = self.ue()
        self.params["slice_type"] = NalUnit.slice_types[self.params["slice_type_int"]]
        self.params["pic_parameter_set_id"] = self.ue()
        self.pps = self.pps[self.params["pic_parameter_set_id"]]
        if self.sps["separate_colour_plane_flag"] == 1 :
            self.params["colour_plane_id"] = self.u(2)
        self.params["frame_num"] = self.u(self.sps["log2_max_frame_num_minus4"] + 4)
        if self.sps["frame_mbs_only_flag"] == 0 :
            self.params["field_pic_flag"] = self.u(1)
            if self.params["field_pic_flag"] > 0 :
                self.params["bottom_field_flag"] = self.u(1)
        else:
            self.params["field_pic_flag"] = 0
        if self.var["IdrPicFlag"] :
            self.params["idr_pic_id"] = self.ue()
        if self.sps["pic_order_cnt_type"] == 0 :
            self.params["pic_order_cnt_lsb"] = \
                self.u(self.sps["log2_max_pic_order_cnt_lsb_minus4"] + 4)
            if (self.pps["bottom_field_pic_order_in_frame_present_flag"] > 0) and \
               (self.params["field_pic_flag"] == 0) :
                self.params["delta_pic_order_cnt_bottom"] = self.se()
        self.params["delta_pic_order_cnt"] = []
        if (self.sps["pic_order_cnt_type"] == 1) and \
           (self.params["delta_pic_order_always_zero_flag"] == 0) :
            self.params["delta_pic_order_cnt"].append(self.se())
            if self.params["bottom_field_pic_order_in_frame_present_flag"] and (not self.params["field_pic_flag"]) :
                self.params["delta_pic_order_cnt"].append(self.se())
        if self.pps["redundant_pic_cnt_present_flag"] > 0 :
            self.params["redundant_pic_cnt"] = self.ue()
        if self.params["slice_type"] == "B" :
            self.params["direct_spatial_mv_pred_flag"] = self.u(1)
        if self.params["slice_type"] == "P" or self.params["slice_type"] == "SP" or self.params["slice_type"] == "B" :
            self.params["num_ref_idx_active_override_flag"] = self.u(1)
            if self.params["num_ref_idx_active_override_flag"] > 0 :
                self.params["num_ref_idx_l0_active_minus1"] = self.ue()
                if self.params["slice_type"] == "B" :
                    self.params["num_ref_idx_l1_active_minus1"] = self.ue()
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
            self.params["cabac_init_idc"] = self.ue()
        self.params["slice_qp_delta"] = self.se()
        if (self.params["slice_type"] == "SP") or (self.params["slice_type"] == "SI") :
            if self.params["slice_type"] == "SP" :
                self.params["sp_for_switch_flag"] = self.u(1)
            self.params["slice_qs_delta"] = self.se()
        if self.pps["deblocking_filter_control_present_flag"] :
            self.params["disable_deblocking_filter_idc"] = self.ue()
            if self.params["disable_deblocking_filter_idc"] != 1 :
                self.params["slice_alpha_c0_offset_div2"] = self.se()
                self.params["slice_beta_offset_div2"] = self.se()
        if self.pps["num_slice_groups_minus1"] > 0 and \
           self.params["slice_group_map_type"] >= 3 and \
           self.params["slice_group_map_type"] <= 5:
            #WIP UV
            print("slice_group_change_cycle NOT impl")
            #self.params["slice_group_change_cycle"] = self.u()
        self.var["PrevRefFrameNum"] = 0 if self.params["nal_unit_type"] == 5 else 1 # TO BE FIXED
        self.var["MbaffFrameFlag"] = self.sps["mb_adaptive_frame_field_flag"] and \
                                     (not self.params["field_pic_flag"])
        self.var["PicWidthInMbs"] = self.sps["pic_width_in_mbs_minus1"] + 1
        self.var["PicHeightInMapUnits"] = self.sps["pic_height_in_map_units_minus1"] + 1
        self.var["FrameHeightInMbs"] = ( 2 - self.sps["frame_mbs_only_flag"] ) * self.var["PicHeightInMapUnits"]
        self.var["PicHeightInMbs"] = self.var["FrameHeightInMbs"] / ( 1 + self.params["field_pic_flag"] )
        self.var["PicSizeInMapUnits"] = self.var["PicWidthInMbs"] * self.var["PicHeightInMapUnits"]
        self.var["PicHeightInMbs"] = self.var["FrameHeightInMbs"] / ( 1 + self.params["field_pic_flag"] )
        print("SLICE HEADER:")
        pprint(self.params)

    def ref_pic_list_mvc_modification(self):
        print("ref_pic_list_mvc_modification NOT IMPL")

    def ref_pic_list_modification(self):
        if (self.params["slice_type_int"] % 5 != 2) and (self.params["slice_type_int"] % 5 != 4) :
            self.params["ref_pic_list_modification_flag_l0"] = self.u(1)
            if self.params["ref_pic_list_modification_flag_l0"] :
                while True :
                    self.params["modification_of_pic_nums_idc"] = self.ue()
                    if self.params["modification_of_pic_nums_idc"] == 0 or \
                       self.params["modification_of_pic_nums_idc"] == 1 :
                        self.params["abs_diff_pic_num_minus1"] = self.ue()
                    elif self.params["modification_of_pic_nums_idc"] == 2 :
                        self.params["long_term_pic_num"] = self.ue()
                    if self.params["modification_of_pic_nums_idc"] == 3:
                        break
        if self.params["slice_type_int"] % 5 == 1 :
            self.params["ref_pic_list_modification_flag_l1"] = self.u(1)
            if self.params["ref_pic_list_modification_flag_l1"]: 
                while True :
                    self.params["modification_of_pic_nums_idc"] = self.ue()
                    if (self.params["modification_of_pic_nums_idc"] == 0) or \
                       (self.params["modification_of_pic_nums_idc"] == 1) :
                        self.params["abs_diff_pic_num_minus1"] = self.ue()
                    elif self.params["modification_of_pic_nums_idc"] == 2 :
                        self.params["long_term_pic_num"] = self.ue()
                    if self.params["modification_of_pic_nums_idc"] == 3 :
                        break


    def pred_weight_table(self):
        print("pred_weight_table NOT impl")
        pass

    def dec_ref_pic_marking(self):
        if self.var["IdrPicFlag"] :
            self.params["no_output_of_prior_pics_flag"] = self.u(1)
            self.params["long_term_reference_flag"] = self.u(1)
        else :
            self.params["adaptive_ref_pic_marking_mode_flag"] = self.u(1)
            if self.params["adaptive_ref_pic_marking_mode_flag"] :
                while True :
                    memory_management_control_operation = self.ue()
                    self.params["memory_management_control_operation"] = memory_management_control_operation
                    if memory_management_control_operation == 1 or \
                       memory_management_control_operation == 3 :
                        self.params["difference_of_pic_nums_minus1"] = self.ue()
                    if memory_management_control_operation == 2 :
                        self.params["long_term_pic_num"] = self.ue()
                    if memory_management_control_operation == 3 or \
                       memory_management_control_operation == 6 :
                        self.params["long_term_frame_idx"] = self.ue()
                    if memory_management_control_operation == 4 :
                        self.params["max_long_term_frame_idx_plus1"] = self.ue()
                    if memory_management_control_operation == 0 :
                        break

    def slice_data(self):
        while self.bits.pos % 8 != 0 :
            self.params["cabac_alignment_one_bit"] = self.f(1)
        print("SLICE DATA:")
        # print(self.bits.pos)
        print(self.bits[self.bits.pos:].hex)
        pass


input_file = open("test.264", "rb")
nalus_bit = list(BitStream(input_file).split('0x00000001', bytealigned=True))[1:]
sps = []
pps = []
slices = []
for nalu_bit in nalus_bit:
    nalu = NalUnit(nalu_bit, sps = [] if sps == [] else sps[0], pps = pps)
    if nalu.params["nal_unit_type"] == 7:
        sps.append(nalu.params)
    elif nalu.params["nal_unit_type"] == 8:
        pps.append(nalu.params)
    elif nalu.params["nal_unit_type"] == 1:
        slices.append(nalu.params)
    elif nalu.params["nal_unit_type"] == 5:
        slices.insert(0, nalu.params)

# nalus = [NalUnit(nalu_bit) for nalu_bit in nalus_bit]
input_file.close()

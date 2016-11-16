from nalunit import NalUnit
from pprint import pprint

class SPS(NalUnit):

    def __init__(self, bits, params):
        self.bits = bits
        self.params = params
        self.parse()

    def parse(self):
        self.seq_parameter_set_rbsp()
        # print("SPS:")
        # pprint(self.params)

    def seq_parameter_set_rbsp(self):
        self.seq_parameter_set_data()
        self.sps_not_present()
        self.rbsp_trailing_bits()

    def seq_parameter_set_data(self):
        self.params["profile_idc"] = self.bits.u(8)
        self.params["constraint_set0_flag"] = self.bits.u(1)
        self.params["constraint_set1_flag"] = self.bits.u(1)
        self.params["constraint_set2_flag"] = self.bits.u(1)
        self.params["constraint_set3_flag"] = self.bits.u(1)
        self.params["constraint_set4_flag"] = self.bits.u(1)
        self.params["constraint_set5_flag"] = self.bits.u(1)
        self.params["reserved_zero_2bits"]  = self.bits.u(2)
        self.params["level_idc"] = self.bits.u(8)
        self.params["seq_parameter_set_id"] =  self.bits.ue()
        if self.params["profile_idc"] == 100 or self.params["profile_idc"] == 110 or self.params["profile_idc"] == 122 or self.params["profile_idc"] == 244 or self.params["profile_idc"] == 44 or self.params["profile_idc"] == 83 or self.params["profile_idc"] == 86 or self.params["profile_idc"] == 118 or self.params["profile_idc"] == 128 or self.params["profile_idc"] == 138 or self.params["profile_idc"] == 139 or self.params["profile_idc"] == 134 or self.params["profile_idc"] == 135 :
            raise NameError('sps:26 not impl')
            # self.params["chroma_format_idc"] = self.bits.ue()
            # if self.params["chroma_format_idc"] == 3 :
            #     self.params["separate_colour_plane_flag"] = self.bits.u(1)
            # else :
            #     self.params["separate_colour_plane_flag"] = 0
            # self.params["ChromaArrayType"] = 0 if self.params["separate_colour_plane_flag"] else self.params["chroma_format_idc"]
            # self.params["bit_depth_luma_minus8"] = self.bits.ue()
            # self.params["bit_depth_chroma_minus8"] = self.bits.ue()
            # self.params["qpprime_y_zero_transform_bypass_flag"] = self.bits.u(1)
            # self.params["seq_scaling_matrix_present_flag"] = self.bits.u(1)
            #if  seq_scaling_matrix_present_flag )    self.bits.u(1:
            #for( i = 0; i < ( ( chroma_format_idc != 3 ) ? 8 : 12 ); i++ ) {
            #seq_scaling_list_present_flag[ i ]    self.bits.u(1)
            #if  seq_scaling_list_present_flag[ i ] :
            #if  i < 6 :
            #scaling_list( ScalingList4x4[ i ], 16, UseDefaultScalingMatrix4x4Flag[ i ] )
            #else
            #scaling_list( ScalingList8x8[ i − 6 ], 64, UseDefaultScalingMatrix8x8Flag[ i − 6 ] )
        self.params["log2_max_frame_num_minus4"] = self.bits.ue()
        self.params["pic_order_cnt_type"] = self.bits.ue()
        if self.params["pic_order_cnt_type"] == 0 :
            self.params["log2_max_pic_order_cnt_lsb_minus4"] = self.bits.ue()
        elif self.params["pic_order_cnt_type"] == 1:
            self.params["delta_pic_order_always_zero_flag"] = self.bits.u(1)
            self.params["offset_for_non_ref_pic"] = self.bits.se()
            self.params["offset_for_top_to_bottom_field"] = self.bits.se()
            self.params["num_ref_frames_in_pic_order_cnt_cycle"] = self.bits.ue()
            self.params["offset_for_ref_frame"] = []
            for i in range(self.params["num_ref_frames_in_pic_order_cnt_cycle"]):
                self.params["offset_for_ref_frame"].append(self.se())
        self.params["max_num_ref_frames"] = self.bits.ue()
        self.params["gaps_in_frame_num_value_allowed_flag"] = self.bits.u(1)
        self.params["pic_width_in_mbs_minus1"] = self.bits.ue()
        self.params["pic_height_in_map_units_minus1"] = self.bits.ue()
        self.params["frame_mbs_only_flag"] = self.bits.u(1)
        if not self.params["frame_mbs_only_flag"]:
            self.params["mb_adaptive_frame_field_flag"] = self.bits.u(1)
        else:
            self.params["mb_adaptive_frame_field_flag"] = 0
        self.params["direct_8x8_inference_flag"] = self.bits.u(1)
        self.params["frame_cropping_flag"] = self.bits.u(1)
        if self.params["frame_cropping_flag"]:
            self.params["frame_crop_left_offset"] = self.bits.ue()
            self.params["frame_crop_right_offset"] = self.bits.ue()
            self.params["frame_crop_top_offset"] = self.bits.ue()
            self.params["frame_crop_bottom_offset"] = self.bits.ue()
        self.params["vui_parameters_present_flag"] = self.bits.u(1)
        if self.params["vui_parameters_present_flag"]:
            self.vui_parameters()

    def vui_parameters(self):
        self.params["aspect_ratio_info_present_flag"] = self.bits.u(1)
        if self.params["aspect_ratio_info_present_flag"]:
            self.params["aspect_ratio_idc"] = self.bits.u(8)
            if self.params["aspect_ratio_idc"] == self.var["Extended_SAR"]:
                self.params["sar_width"] = self.bits.u(16)
                self.params["sar_height"] = self.bits.u(16)
        self.params["overscan_info_present_flag"] = self.bits.u(1)
        if self.params["overscan_info_present_flag"]:
            self.params["overscan_appropriate_flag"] = self.bits.u(1)
        self.params["video_signal_type_present_flag"] = self.bits.u(1)
        if self.params["video_signal_type_present_flag"]:
            self.params["video_format"] = self.bits.u(3)
            self.params["video_full_range_flag"] = self.bits.u(1)
            self.params["colour_description_present_flag"] = self.bits.u(1)
            if self.params["colour_description_present_flag"]:
                self.params["colour_primaries"] = self.bits.u(8)
                self.params["transfer_characteristics"] = self.bits.u(8)
                self.params["matrix_coefficients"] = self.bits.u(8)
        self.params["chroma_loc_info_present_flag"] = self.bits.u(1)
        if self.params["chroma_loc_info_present_flag"]:
            self.params["chroma_sample_loc_type_top_field"] = self.bits.ue()
            self.params["chroma_sample_loc_type_bottom_field"] = self.bits.ue()
        self.params["timing_info_present_flag"] = self.bits.u(1)
        if self.params["timing_info_present_flag"]:
            self.params["num_units_in_tick"] = self.bits.u(32)
            self.params["time_scale"] = self.bits.u(32)
            self.params["fixed_frame_rate_flag"] = self.bits.u(1)
        self.params["nal_hrd_parameters_present_flag"] = self.bits.u(1)
        if self.params["nal_hrd_parameters_present_flag"]:
            self.hrd_parameters()
        self.params["vcl_hrd_parameters_present_flag"] = self.bits.u(1)
        if self.params["vcl_hrd_parameters_present_flag"]:
            self.hrd_parameters()
        if self.params["nal_hrd_parameters_present_flag"] or self.params["vcl_hrd_parameters_present_flag"]:
            self.params["low_delay_hrd_flag"] = self.bits.u(1)
        self.params["pic_struct_present_flag"] = self.bits.u(1)
        self.params["bitstream_restriction_flag"] = self.bits.u(1)
        if self.params["bitstream_restriction_flag"]:
            self.params["motion_vectors_over_pic_boundaries_flag"] = self.bits.u(1)
            self.params["max_bytes_per_pic_denom"] = self.bits.ue()
            self.params["max_bits_per_mb_denom"] = self.bits.ue()
            self.params["log2_max_mv_length_horizontal"] = self.bits.ue()
            self.params["log2_max_mv_length_vertical"] = self.bits.ue()
            self.params["max_num_reorder_frames"] = self.bits.ue()
            self.params["max_dec_frame_buffering"] = self.bits.ue()

    def hrd_parameters(self):
        self.params["cpb_cnt_minus1"] = self.bits.ue()
        self.params["bit_rate_scale"] = self.bits.u(4)
        self.params["cpb_size_scale"] = self.bits.u(4)

        self.params["bit_rate_value_minus1"] = []
        self.params["cpb_size_value_minus1"] = []
        self.params["cbr_flag"] = []
        for SchedSelIdx in range(self.params["cpb_cnt_minus1"] + 1):
            self.params["bit_rate_value_minus1"].append(self.bits.ue())
            self.params["cpb_size_value_minus1"].append(self.bits.ue())
            self.params["cbr_flag"].append(self.bits.u(1))
        self.params["initial_cpb_removal_delay_length_minus1"] = self.bits.u(5)
        self.params["cpb_removal_delay_length_minus1"] = self.bits.u(5)
        self.params["dpb_output_delay_length_minus1"] = self.bits.u(5)
        self.params["time_offset_length"] = self.bits.u(5)

    def sps_not_present(self):
        keys = self.params.keys()
        if "chroma_format_idc" not in keys:
            self.params["chroma_format_idc"] = 1
        if "separate_colour_plane_flag" not in keys:
            self.params["separate_colour_plane_flag"] = 0
            self.params["ChromaArrayType"] = self.params["chroma_format_idc"]
        if self.params["chroma_format_idc"] == 1 and self.params["separate_colour_plane_flag"] == 0:
            self.params["SubWidthC"] = 2
            self.params["SubHeightC"] = 2
        elif self.params["chroma_format_idc"] == 2 and self.params["separate_colour_plane_flag"] == 0:
            self.params["SubWidthC"] = 2
            self.params["SubHeightC"] = 1
        elif self.params["chroma_format_idc"] == 3 and self.params["separate_colour_plane_flag"] == 0:
            self.params["SubWidthC"] = 1
            self.params["SubHeightC"] = 1
        if self.params["chroma_format_idc"] == 0 or self.params["separate_colour_plane_flag"] == 1:
            self.params["MbWidthC"] = 0
            self.params["MbHeightC"] = 0
        else:
            self.params["MbWidthC"] = 16 // self.params["SubWidthC"]
            self.params["MbHeightC"] = 16 // self.params["SubHeightC"]
        if "bit_depth_luma_minus8" not in keys:
            self.params["bit_depth_luma_minus8"] = 0
        if "bit_depth_chroma_minus8" not in keys:
            self.params["bit_depth_chroma_minus8"] = 0
        if "qpprime_y_zero_transform_bypass_flag" not in keys:
            self.params["qpprime_y_zero_transform_bypass_flag"] = 0
        if "mb_adaptive_frame_field_flag" not in keys:
            self.params["mb_adaptive_frame_field_flag"] = 0

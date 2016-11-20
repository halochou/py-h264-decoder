from nalunit import NalUnit
from pprint import pprint

class SPS:

    def __init__(self, bits, params):
        self.bits = bits
        for k in params:
            self.__dict__[k] = params[k]
        self.parse()

    def rbsp_trailing_bits(self):
        # if self.bits.more_data():
        self.rbsp_stop_one_bit = self.bits.f(1)
        assert self.rbsp_stop_one_bit == 1
        # self.params["rbsp_alignment_zero_bit"] = self.bits[self.bits.pos:].int
        while not self.bits.byte_aligned():
            assert self.bits.f(1) == 0  

    def parse(self):
        self.seq_parameter_set_rbsp()
        # print("SPS:")
        # pprint(self.params)

    def seq_parameter_set_rbsp(self):
        self.seq_parameter_set_data()
        self.sps_not_present()
        self.rbsp_trailing_bits()

    def seq_parameter_set_data(self):
        self.profile_idc = self.bits.u(8)
        self.constraint_set0_flag = self.bits.u(1)
        self.constraint_set1_flag = self.bits.u(1)
        self.constraint_set2_flag = self.bits.u(1)
        self.constraint_set3_flag = self.bits.u(1)
        self.constraint_set4_flag = self.bits.u(1)
        self.constraint_set5_flag = self.bits.u(1)
        self.reserved_zero_2bits  = self.bits.u(2)
        self.level_idc = self.bits.u(8)
        self.seq_parameter_set_id =  self.bits.ue()
        if self.profile_idc == 100 or self.profile_idc == 110 or self.profile_idc == 122 or self.profile_idc == 244 or self.profile_idc == 44 or self.profile_idc == 83 or self.profile_idc == 86 or self.profile_idc == 118 or self.profile_idc == 128 or self.profile_idc == 138 or self.profile_idc == 139 or self.profile_idc == 134 or self.profile_idc == 135 :
            raise NameError('sps:26 not impl')
            # self.chroma_format_idc = self.bits.ue()
            # if self.chroma_format_idc == 3 :
            #     self.separate_colour_plane_flag = self.bits.u(1)
            # else :
            #     self.separate_colour_plane_flag = 0
            # self.ChromaArrayType = 0 if self.separate_colour_plane_flag else self.chroma_format_idc
            # self.bit_depth_luma_minus8 = self.bits.ue()
            # self.bit_depth_chroma_minus8 = self.bits.ue()
            # self.qpprime_y_zero_transform_bypass_flag = self.bits.u(1)
            # self.seq_scaling_matrix_present_flag = self.bits.u(1)
            #if  seq_scaling_matrix_present_flag )    self.bits.u(1:
            #for( i = 0; i < ( ( chroma_format_idc != 3 ) ? 8 : 12 ); i++ ) {
            #seq_scaling_list_present_flag[ i ]    self.bits.u(1)
            #if  seq_scaling_list_present_flag[ i ] :
            #if  i < 6 :
            #scaling_list( ScalingList4x4[ i ], 16, UseDefaultScalingMatrix4x4Flag[ i ] )
            #else
            #scaling_list( ScalingList8x8[ i − 6 ], 64, UseDefaultScalingMatrix8x8Flag[ i − 6 ] )
        self.log2_max_frame_num_minus4 = self.bits.ue()
        self.pic_order_cnt_type = self.bits.ue()
        if self.pic_order_cnt_type == 0 :
            self.log2_max_pic_order_cnt_lsb_minus4 = self.bits.ue()
        elif self.pic_order_cnt_type == 1:
            self.delta_pic_order_always_zero_flag = self.bits.u(1)
            self.offset_for_non_ref_pic = self.bits.se()
            self.offset_for_top_to_bottom_field = self.bits.se()
            self.num_ref_frames_in_pic_order_cnt_cycle = self.bits.ue()
            self.offset_for_ref_frame = []
            for i in range(self.num_ref_frames_in_pic_order_cnt_cycle):
                self.offset_for_ref_frame.append(self.se())
        self.max_num_ref_frames = self.bits.ue()
        self.gaps_in_frame_num_value_allowed_flag = self.bits.u(1)
        self.pic_width_in_mbs_minus1 = self.bits.ue()
        self.pic_height_in_map_units_minus1 = self.bits.ue()
        self.frame_mbs_only_flag = self.bits.u(1)
        if not self.frame_mbs_only_flag:
            self.mb_adaptive_frame_field_flag = self.bits.u(1)
        else:
            self.mb_adaptive_frame_field_flag = 0
        self.direct_8x8_inference_flag = self.bits.u(1)
        self.frame_cropping_flag = self.bits.u(1)
        if self.frame_cropping_flag:
            self.frame_crop_left_offset = self.bits.ue()
            self.frame_crop_right_offset = self.bits.ue()
            self.frame_crop_top_offset = self.bits.ue()
            self.frame_crop_bottom_offset = self.bits.ue()
        self.vui_parameters_present_flag = self.bits.u(1)
        if self.vui_parameters_present_flag:
            self.vui_parameters()

    def vui_parameters(self):
        self.aspect_ratio_info_present_flag = self.bits.u(1)
        if self.aspect_ratio_info_present_flag:
            self.aspect_ratio_idc = self.bits.u(8)
            if self.aspect_ratio_idc == self.Extended_SAR:
                self.sar_width = self.bits.u(16)
                self.sar_height = self.bits.u(16)
        self.overscan_info_present_flag = self.bits.u(1)
        if self.overscan_info_present_flag:
            self.overscan_appropriate_flag = self.bits.u(1)
        self.video_signal_type_present_flag = self.bits.u(1)
        if self.video_signal_type_present_flag:
            self.video_format = self.bits.u(3)
            self.video_full_range_flag = self.bits.u(1)
            self.colour_description_present_flag = self.bits.u(1)
            if self.colour_description_present_flag:
                self.colour_primaries = self.bits.u(8)
                self.transfer_characteristics = self.bits.u(8)
                self.matrix_coefficients = self.bits.u(8)
        self.chroma_loc_info_present_flag = self.bits.u(1)
        if self.chroma_loc_info_present_flag:
            self.chroma_sample_loc_type_top_field = self.bits.ue()
            self.chroma_sample_loc_type_bottom_field = self.bits.ue()
        self.timing_info_present_flag = self.bits.u(1)
        if self.timing_info_present_flag:
            self.num_units_in_tick = self.bits.u(32)
            self.time_scale = self.bits.u(32)
            self.fixed_frame_rate_flag = self.bits.u(1)
        self.nal_hrd_parameters_present_flag = self.bits.u(1)
        if self.nal_hrd_parameters_present_flag:
            self.hrd_parameters()
        self.vcl_hrd_parameters_present_flag = self.bits.u(1)
        if self.vcl_hrd_parameters_present_flag:
            self.hrd_parameters()
        if self.nal_hrd_parameters_present_flag or self.vcl_hrd_parameters_present_flag:
            self.low_delay_hrd_flag = self.bits.u(1)
        self.pic_struct_present_flag = self.bits.u(1)
        self.bitstream_restriction_flag = self.bits.u(1)
        if self.bitstream_restriction_flag:
            self.motion_vectors_over_pic_boundaries_flag = self.bits.u(1)
            self.max_bytes_per_pic_denom = self.bits.ue()
            self.max_bits_per_mb_denom = self.bits.ue()
            self.log2_max_mv_length_horizontal = self.bits.ue()
            self.log2_max_mv_length_vertical = self.bits.ue()
            self.max_num_reorder_frames = self.bits.ue()
            self.max_dec_frame_buffering = self.bits.ue()

    def hrd_parameters(self):
        self.cpb_cnt_minus1 = self.bits.ue()
        self.bit_rate_scale = self.bits.u(4)
        self.cpb_size_scale = self.bits.u(4)

        self.bit_rate_value_minus1 = []
        self.cpb_size_value_minus1 = []
        self.cbr_flag = []
        for SchedSelIdx in range(self.cpb_cnt_minus1 + 1):
            self.bit_rate_value_minus1.append(self.bits.ue())
            self.cpb_size_value_minus1.append(self.bits.ue())
            self.cbr_flag.append(self.bits.u(1))
        self.initial_cpb_removal_delay_length_minus1 = self.bits.u(5)
        self.cpb_removal_delay_length_minus1 = self.bits.u(5)
        self.dpb_output_delay_length_minus1 = self.bits.u(5)
        self.time_offset_length = self.bits.u(5)

    def sps_not_present(self):
        keys = self.__dict__.keys()
        if "chroma_format_idc" not in keys:
            self.chroma_format_idc = 1
        if "separate_colour_plane_flag" not in keys:
            self.separate_colour_plane_flag = 0
            self.ChromaArrayType = self.chroma_format_idc
        if self.chroma_format_idc == 1 and self.separate_colour_plane_flag == 0:
            self.SubWidthC = 2
            self.SubHeightC = 2
        elif self.chroma_format_idc == 2 and self.separate_colour_plane_flag == 0:
            self.SubWidthC = 2
            self.SubHeightC = 1
        elif self.chroma_format_idc == 3 and self.separate_colour_plane_flag == 0:
            self.SubWidthC = 1
            self.SubHeightC = 1
        if self.chroma_format_idc == 0 or self.separate_colour_plane_flag == 1:
            self.MbWidthC = 0
            self.MbHeightC = 0
        else:
            self.MbWidthC = 16 // self.SubWidthC
            self.MbHeightC = 16 // self.SubHeightC
        if "bit_depth_luma_minus8" not in keys:
            self.bit_depth_luma_minus8 = 0
            self.BitDepth_Y = 8 + self.bit_depth_luma_minus8
            self.QpBdOffset_Y = 6 * self.bit_depth_luma_minus8
        if "bit_depth_chroma_minus8" not in keys:
            self.bit_depth_chroma_minus8 = 0
            self.BitDepth_C = 8 + self.bit_depth_chroma_minus8
            self.QpBdOffset_C = 6 * self.bit_depth_chroma_minus8
        if "qpprime_y_zero_transform_bypass_flag" not in keys:
            self.qpprime_y_zero_transform_bypass_flag = 0
        if "mb_adaptive_frame_field_flag" not in keys:
            self.mb_adaptive_frame_field_flag = 0

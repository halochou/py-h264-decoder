dec_ref_pic_marking( ) {
    if( IdrPicFlag ) {
        no_output_of_prior_pics_flag
        long_term_reference_flag
    } else {
        adaptive_ref_pic_marking_mode_flag
        if( adaptive_ref_pic_marking_mode_flag )
            do {
                memory_management_control_operation
                if( memory_management_control_operation = = 1 | | memory_management_control_operation = = 3 )
                    difference_of_pic_nums_minus1
                if(memory_management_control_operation = = 2 )
                    long_term_pic_num
                if( memory_management_control_operation = = 3 | | memory_management_control_operation = = 6 )
                    long_term_frame_idx
                if( memory_management_control_operation = = 4 )
                    max_long_term_frame_idx_plus1
            } while( memory_management_control_operation != 0 )
        }
    }
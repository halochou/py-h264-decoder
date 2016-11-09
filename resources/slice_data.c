slice_data( ) {
    if( entropy_coding_mode_flag )
        while( !byte_aligned( ) )
            cabac_alignment_one_bit
    CurrMbAddr = first_mb_in_slice * ( 1 + MbaffFrameFlag )
    moreDataFlag = 1
    prevMbSkipped = 0
    do {
        if( slice_type != I && slice_type != SI )
            if( !entropy_coding_mode_flag ) {
                mb_skip_run
                prevMbSkipped = ( mb_skip_run > 0 )
                for( i=0; i<mb_skip_run; i++ )
                    CurrMbAddr = NextMbAddress( CurrMbAddr )
                if( mb_skip_run > 0 )
                    moreDataFlag = more_rbsp_data( )
            } else {
                mb_skip_flag
                moreDataFlag = !mb_skip_flag
            }
        if( moreDataFlag ) {
            if( MbaffFrameFlag && ( CurrMbAddr % 2 = = 0 | | ( CurrMbAddr % 2 = = 1 && prevMbSkipped ) ) )
                mb_field_decoding_flag
            macroblock_layer( )
        }
        if( !entropy_coding_mode_flag )
            moreDataFlag = more_rbsp_data( )
        else {
            if( slice_type != I && slice_type != SI )
                prevMbSkipped = mb_skip_flag
            if( MbaffFrameFlag && CurrMbAddr % 2 = = 0 )
                moreDataFlag = 1
            else {
                end_of_slice_flag
                moreDataFlag = !end_of_slice_flag
            }
        }
        CurrMbAddr = NextMbAddress( CurrMbAddr )
    } while( moreDataFlag )
}
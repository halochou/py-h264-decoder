# 6.4.1 Inverse macroblock scanning process
def get_cord_of_mb(mbAddr, MbaffFrameFlag, PicWidthInSamples_L):
    x = InverseRasterScan( mbAddr, 16, 16, PicWidthInSamples_L , 0 )
    y = InverseRasterScan( mbAddr, 16, 16, PicWidthInSamples_L , 1 )

# 6.4.3 Inverse 4x4 luma block scanning process
def get_cord_of_luma4x4(luma4x4BlkIdx):
    x = InverseRasterScan( luma4x4BlkIdx // 4, 8, 8, 16, 0 ) + InverseRasterScan( luma4x4BlkIdx % 4, 4, 4, 8, 0 )
    y = InverseRasterScan( luma4x4BlkIdx // 4, 8, 8, 16, 1 ) + InverseRasterScan( luma4x4BlkIdx % 4, 4, 4, 8, 1 )
    return (x, y)

# 8.5 Construct One MB sample array, S'L S'Cb S'Cr
def construct_picture(coeffLevels, predSamples):
    assert False

# 8.5.1 transform decoding process for 4x4 luma residual blocks
def dec_luma4x4(luma4x4BlkIdx):
    c = inv_scan_for_4x4_coeff_slist(coeffLevels)
    r = idct_and_scaling_for_4x4(c)
    if TransformByassert FalseModeFlag == 1:
        raise NameError("8.5.1-3 TransformByassert FalseModeFlag not impl")
    (xO, yO) = get_cord_of_luma4x4(luma4x4BlkIdx)
    u = [[None]*4]*4
    for i in range(4):
        for j in range(4):
            u[i][j] = [Clip1_Y(pred_L[xO+j, yO+i] + r[i][j])]
    pic_construct(u, luma4x4BlkIdx)

# 8.5.2 transform decoding process for luma samples of Intra_16x16 macroblock prediction mode
def idct_for_luma16x16():
    assert False

# 8.5.3 transform decoding process for 8x8 luma residual blocks
def idct_for_luma8x8():
    assert False

# 8.5.4 transform decoding process for chroma samples
def idct_for_chroma():
    assert False

# 8.5.5 transform decoding process for chroma samples with ChromaArrayType equal to 3

# 8.5.6 Inverse scanning process for 4x4 transform coefficients and scaling lists
def inv_scan_for_4x4_coeff_slist(arr):
    zigzag = [(0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (0, 3), (1, 2), (2, 1), (3, 0), (3, 1), (2, 2), (1, 3), (2, 3), (3, 2), (3, 3)]
    c = [[None]*4]*4
    for (idx, v) in enumerate(arr):
        (x, y) = zigzag[idx]
        c[x][y] = v
    return c

# 8.5.7 Inverse scanning process for 8x8 transform coefficients and scaling lists
def inv_scan_for_8x8():
    assert False

# 8.5.8 Derivation process for chroma quantisation parameters
def get_chroma_qp():
    assert False

# 8.5.9 Derivation process for scaling functions
def get_4x4_scaling_fn(mb_pred_mode, separate_colour_plane_flag, mode):
    mbIsInterFlag = 1 if "Inter" in mb_pred_mode else 0
    iYCbCr = colour_plane_id if separate_colour_plane_flag == 1 else ["Y", "Cb", "Cr"].index(mode)
    weightScale4x4 = inv_scan_for_4x4_coeff_slist(ScalingList4x4[iYCbCr + (3 if mbIsInterFlag == 1 else 0)])
    LevelScale4x4 = [[[None]*6]*4]*4
    for i in range(4):
        for j in range(4):
            LevelScale4x4[m][i][j] = weightScale4x4[i][j] * normAdjust4x4(m, i, j)
    # LevelScale8x8 not impl
    return LevelScale4x4
def normAdjust4x4(m, i, j):
    v = [[10,16,13],
         [11,18,14],
         [13,20,16],
         [14,23,18],
         [16,25,20],
         [18,29,23]]
    if (i%2, j%2) == (0, 0):
        return v[m][0]
    elif (i%2, j%2) == (1, 1):
        return v[m][1]
    else:
        return v[m][2]

# 8.5.10 Scaling and transformation process for DC transform coefficients for Intra_16x16 macroblock type
def idct_for_dc_luma_16x16():
    assert False

# 8.5.11 Scaling and transformation process for chroma DC transform coefficients
def idct_and_scaling_for_dc_chroma():
    assert False

# 8.5.11.1 Transformation process for chroma DC transform coefficients
def idct_for_dc_chroma():
    assert False

# 8.5.11.2 Scaling process for chroma DC transform coefficients
def scaling_for_dc_chroma():
    assert False

# 8.5.12 Scaling and transformation process for residual 4x4 blocks
def idct_and_scaling_for_4x4(c, mode):
    bitDepth = BitDepth_Y if mode == "Y" else BitDepth_C
    sMbFlag = 0 # maybe bug
    if mode == "Y" and sMbFlag == 0:
        qP = QP_prime_Y
    elif mode in ["Cb", "Cr"] and sMbFlag == 0:
        qp = QP_prime_C
    else:
        raise NameError("sMbFlag not impl")
    if TransformBypassModeFlag == 1:
        raise NameError("sMbFlag not impl")
    else:
        d = scaling_for_4x4(bitDepth, qP, c)
        r = idct_for_4x4(bitDepth, d)
    return r

# 8.5.12.1 Scaling process for residual 4x4 blocks
def scaling_for_4x4(bitDepth, qP, c, mode, pred):
    d = [[None]*4]*4
    if (mode == "Y" and "Intra_16x16" in pred_mode) or mode in ["Cb","Cr"]:
        d[0][0] = c[0][0]
    if qP >= 24:
        for i in range(4):
            for j in range(4):
                d[i][j] = (c[i][j] * LevelScale4x4[qP%6, i, j]) << (qP/6−4)
    else:
        for i in range(4):
            for j in range(4):
                d[i][j] = (c[i][j] * LevelScale4x4[qP%6, i, j] + 2**(3-qp//6)) >> (4 - qp//6)
    if (mode == "Y" and "Intra_16x16" in pred_mode) or mode in ["Cb","Cr"]:
        d[0][0] = c[0][0]
    return d

# 8.5.12.2 Transformation process for residual 4x4 blocks
def idct_for_4x4(bitDepth, d):
    e = [[None]*4]*4
    for i in range(4):
        e[i][0] = d[i][0] + d[i][2]
        e[i][1] = d[i][0] - d[i][2]
        e[i][2] = (d[i][1] >> 1) - d[i][3]
        e[i][3] = d[i][1] + (d[i][3] >> 1)
    f = [[None]*4]*4
    for i in range(4):
        f[i][0] = e[i][0] + e[i][3]
        f[i][1] = e[i][1] + e[i][2]
        f[i][2] = e[i][1] - e[i][2]
        f[i][3] = e[i][0] - e[i][3]
    g = [[None]*4]*4
    for j in range(4):
        g[0][j] = f[0][j] + f[2][j]
        g[1][j] = f[0][j] - f[2][j]
        g[2][j] = (f[1][j] >> 1) - f[3][j]
        g[3][j] = f[1][j] + (f[3][j] >> 1)
    h = [[None]*4]*4
    for j in range(4):
        h[0][j] = g[0][j] + g[3][j]
        h[1][j] = g[1][j] + g[2][j]
        h[2][j] = g[1][j] - g[2][j]
        h[3][j] = g[0][j] - g[3][j]
    r = [[None]*4]*4
    for i in range(4):
        for j in range(4):
            r[i][j] = (h[i][j] + 2**5) >> 6
    return r

# 8.5.13 Scaling and transformation process for residual 8x8 blocks
def idct_and_scaling_for_8x8():
    assert False
# 8.5.13.1 Scaling process for residual 8x8 blocks
def scaling_for_8x8():
    assert False
# 8.5.13.2 Transformation process for residual 8x8 blocks
def idct_for_8x8():
    assert False

# 8.5.14 Picture construction process
def pic_construct(u, idx, mode):
    if mode == "Luma":
        (xP, yP) = get_cord_of_mb(CurrMbAddr, MbaffFrameFlag, PicWidthInSamples_L)
        if mode == "Luma16x16":
            (xO, yO) = (0, 0)
            nE = 16
        elif mode == "Luma4x4":
            (xO, yO) = get_cord_of_luma4x4(idx)
            nE = 8
        elif mode == "Luma8x8":
            raise NameError("8x8 not impl")
        if MbaffFrameFlag == 0:
            S_L = [[None]*nE]*nE
            for i in range(nE):
                for j in range(nE):
                    S_L[xP+xO+j, yP+yO+i] = u[i][j]
    else:
        raise NameError("Chroma not impl")

# 8.5.15 Intra residual transform-byassert False decoding process
def tran_byp():
    assert False
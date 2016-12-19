# H.264 Baseline Decoder

This project is for uOttawa course ELG5126 and is able to decode YCbCr values from i-frame in H.264 Baseline profile raw bitstream.

The program is written in Python 3.5, so you will need to install Python 3.5 or above together with dependency:

    bitstring 3.1.5

which is recommended to be installed by pip:

    pip3 install bitstring

The program can be executed as:

    python3 decoder.py


Description of files:

    .
    ├── README.md           # This readme file
    ├── baseline.264        # Foreman QCIF test file in raw H.264 bitstream
    ├── block.py            # Class Block
    ├── decoder.py          # Main program entrance
    ├── h264bits.py         # Class H264Bits 
    ├── idct.py             # Module for inverse DCT and scaling
    ├── intra_pred.py       # Module for intra prediction
    ├── macroblock.py       # Class Macroblock
    ├── nalpps.py           # Class PPS
    ├── nalslice.py         # Class Slice
    ├── nalsps.py           # Class SPS
    ├── nalunit.py          # Class NALU
    ├── output.png          # Output I-Frame image
    ├── pps_1.json          # Output file for PPS parameters
    ├── slice_1.json        # Output file for Slice parameters
    ├── slice_1_mb.json     # Output file for MB coefficients
    ├── sps.json            # Output f# Output file for SPS parameters
    ├── utilities.py        # Module utility functions
    └── viewer.m            # YCbCr to RGB converter in Matlab
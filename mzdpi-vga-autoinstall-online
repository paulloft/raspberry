#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "Installing must be run as root" 1>&2
   exit 1
fi

do_dts_dtb() {
# now create dts file
echo "Creating mzdpi.dts overlay..."
cat <<\EOF > /boot/overlays/mzdpi.dts && 
/dts-v1/;
/plugin/;


/ {
    compatible = "brcm,bcm2835", "brcm,bcm2708", "brcm,bcm2709";

    fragment@0 {
        target = <&spi0_pins>;
        __overlay__ {
            brcm,pins = <37 38 39>;
            brcm,function = <4>;     /* alt0 was <3> alt4 */
        };
    };

    fragment@1 {
        target = <&spi0_cs_pins>;
        frag1: __overlay__ {
            brcm,pins = <36>;
            brcm,function = <1>; /* output */
        };
    };

    fragment@2 {
        target = <&spidev0>;
        frag2: __overlay__ {
            status = "okay";
        };
    };

    fragment@3 {
        target = <&spidev1>;
        __overlay__ {
            status = "disabled";
        };
    };

    fragment@4 {
        target = <&spi0>;
        frag4: __overlay__ {
            /* needed to avoid dtc warning */
            #address-cells = <1>;
            #size-cells = <0>;
            cs-gpios = <&gpio 36 1>;
            status = "okay";
        };
    };

    fragment@5 {
        target = <&aux>;
        __overlay__ {
            status = "okay";
        };
    };

    __overrides__ {
        cs0_pin  = <&frag1>,"brcm,pins:0",
               <&frag4>,"cs-gpios:4";
        cs0_spidev = <&frag2>,"status";
    };
};
EOF
dtc -W no-unit_address_vs_reg -I dts -O dtb -o /boot/overlays/mzdpi.dtbo /boot/overlays/mzdpi.dts
}

do_create_conf() {
echo "Creating calibration config..."
if [ -f "/etc/X11/xorg.conf.d/99-calibration.conf" ];then
	echo "Already exist. skipped"
	return
fi

mkdir /etc/X11/xorg.conf.d
cat <<EOF > /etc/X11/xorg.conf.d/99-calibration.conf 
Section "InputClass"
	Identifier	"calibration"
	MatchProduct	"ADS7846 Touchscreen"
	Option	"Calibration"	"195 3895 240 3813"
	Option	"SwapAxes"	"0"
EndSection

EOF

}

apt-get install -y xserver-xorg-input-evdev
apt-get install -y xinput-calibrator

if [ -f "/usr/share/X11/xorg.conf.d/40-libinput.conf" ];then
	mv /usr/share/X11/xorg.conf.d/40-libinput.conf /usr/share/X11/xorg.conf.d/40-libinput.bak
fi

apt-get install -y matchbox-keyboard

do_create_conf
do_dts_dtb

echo "Updating boot config..."
cp /boot/config.txt /boot/tmp.txt

sed  -i "/gpio=18=/d" /boot/tmp.txt
sed  -i "/dtparam=spi=/d" /boot/tmp.txt
sed  -i "/dtoverlay=ads7846/d" /boot/tmp.txt
sed  -i "/display_rotate=/d" /boot/tmp.txt
sed  -i "/dtoverlay=mzdpi/d" /boot/tmp.txt
sed  -i "/framebuffer_width=/d" /boot/tmp.txt
sed  -i "/framebuffer_height=/d" /boot/tmp.txt
sed  -i "/enable_dpi_lcd=/d" /boot/tmp.txt
sed  -i "/display_default_lcd=/d" /boot/tmp.txt
sed  -i "/dpi_group=/d" /boot/tmp.txt
sed  -i "/dpi_mode=/d" /boot/tmp.txt
sed  -i "/dpi_output_format=/d" /boot/tmp.txt
sed  -i "/hdmi_timings=/d" /boot/tmp.txt

echo "gpio=18=op,dh" >> /boot/tmp.txt
echo "dtparam=spi=on" >> /boot/tmp.txt
echo "dtoverlay=ads7846,penirq=27,swapxy=1,xmin=200,xmax=3850,ymin=200,ymax=3850" >> /boot/tmp.txt
echo "display_rotate=3" >> /boot/tmp.txt
echo "dtoverlay=mzdpi" >> /boot/tmp.txt
echo "framebuffer_width=640" >> /boot/tmp.txt
echo "framebuffer_height=480" >> /boot/tmp.txt
echo "enable_dpi_lcd=1" >> /boot/tmp.txt
echo "display_default_lcd=1" >> /boot/tmp.txt
echo "dpi_group=2" >> /boot/tmp.txt
echo "dpi_mode=87" >> /boot/tmp.txt
echo "dpi_output_format=0x07f003" >> /boot/tmp.txt
echo "hdmi_timings=480 0 41 20 60 640 0 5 10 10 0 0 0 60 0 32000000 1" >> /boot/tmp.txt

cp /boot/tmp.txt /boot/config.txt
echo "DONE"

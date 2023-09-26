#!/usr/bin/env sh
set -- $(locale LC_MESSAGES)
yesptrn="$1"; noptrn="$2"; yesword="$3"; noword="$4"

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

input_sink=$(pacmd stat |grep -o -P "(?<=Default source name: ).*")
output_sink=$(pacmd stat |grep -o -P "(?<=Default sink name: ).*")

echo "Input:" $input_sink
echo "Output:" $output_sink
echo "If those arent the sinks you want to use change the default input/output in pavucontroll or similiar and restart this script"


ladspa_file=$parent_path/bin/ladspa/librnnoise_ladspa.so

if [ -f "$ladspa_file" ]; then
    echo "$ladspa_file found."
else 
    echo -e "$ladspa_file does not exist. Downloading now: \n"
	wget https://github.com/werman/noise-suppression-for-voice/releases/download/v0.2/linux_rnnoise_bin_x64.tar.gz -P $parent_path
	tar xf $parent_path/linux_rnnoise_bin_x64.tar.gz -C $parent_path
	rm $parent_path/linux_rnnoise_bin_x64.tar.gz

	if [ -f "$ladspa_file" ]; then
    	echo -e "\n $ladspa_file now found."
	else
		echo -e "\n couldn't download file. Please check output."
		exit
	fi
fi

pacmd load-module module-null-sink sink_name=mic_denoised_out
pacmd load-module module-ladspa-sink sink_name=mic_raw_in sink_master=mic_denoised_out label=noise_suppressor_mono plugin=$ladspa_file
pacmd load-module module-loopback latency_msec=1 source=$input_sink sink=mic_raw_in channels=1

pacmd set-default-source mic_denoised_out.monitor


while true; do
    read -p "Do you want to hear yourself? (${yesword} / ${noword})? " yn
    case $yn in
        ${yesword} ) 
			pacmd load-module module-loopback latency_msec=1 source=mic_denoised_out.monitor sink=$output_sink ; break;;
        ${noword} )  break;;
        * ) echo "Answer ${yesword} / ${noword}.";;
    esac
done


while true; do
    read -p "Do you want to unload the custom filter? (${yesword} / ${noword})? " yn
    case $yn in
        ${yesword} ) 
			pactl unload-module module-loopback
			pactl unload-module module-null-sink
			pactl unload-module module-ladspa-sink
			break;;
        ${noword} ) exit;;
        * ) echo "Answer ${yesword} / ${noword}.";;
    esac
done




# Fast loopback device (very cpu hungry)
# pacat -r --latency-msec=1 -d alsa_input.usb-0d8c_C-Media_USB_Audio_Device-00.mono-fallback | pacat -p --latency-msec=1 -d alsa_output.usb-0d8c_C-Media_USB_Audio_Device-00.analog-stereo

#!/bin/bash

VID="0D28"
EXPECT_MODEL="MBED_CMSIS-DAP"
EXPECT_LABEL="MBED"

if [ $# != 1 ]; then
	echo "This program will program new firmware into an mbed board"
	echo ""
	echo "$0 <path to new firmware>"
	exit 1
fi

bin="$1"

if [ ! -f "$bin" ]; then
	echo "Cannot open firmware file $bin"
	exit 2
fi


echo "Searching for mbed board..."

# lsusb -d will return output like this:
# Bus 007 Device 002: ID 04cc:0003 Philips Semiconductors 
lsusb -d "${VID}:" |
#                  Bus  007 Device 002:   ID   04cc:0003 Philips Semiconductors
while IFS=" " read lab1 bus lab2   device lab3 id        mfg
do
	device="${device:0:3}" # remove trailing ':' from device number
	echo "Found USB bus number: $bus device number: $device"

	# make udev path for USB device
	path="/dev/bus/usb/$bus/$device"
	echo "Linux UDEV device path should be: $path"
	echo "Now reading USB device info."

	# read USB model ID for that device using udevadm
	model=$(udevadm info -q property -n $path | grep ID_MODEL=)
	model="${model:9}"
	echo "Device Model ID is $model"
	if [ $model != "${EXPECT_MODEL}" ]; then
		echo "Model does not match: Not \"${EXPECT_MODEL}\""
	else
		echo "Correct model ID found."
		echo "Searching for disk devices with matching device path..."

		# convert our udev path into a much longer kernel device filename
		devpath=$(udevadm info -q path -n $path)

		# iterate through all of the disk devices, assuming they start with
		# sd and have one letter in them.
		for disk in /dev/sd[a-z]; do
			echo "Checking disk $disk..."
			# run udevadm again to get the kernel device filename for
			# the disk device we are checking.
			diskdevpath=$(udevadm info -q path -n $disk)
			# test to see if the disk device's kernel file matches the
			# USB device's kernel file
			if [ $devpath = ${diskdevpath:0:${#devpath}} ]; then
				echo "Match found: Disk device is $disk"
				# We found the disk for our USB device. Now test to
				# see if we can find it in the mount command output.
				# /dev/sdc on /media/CRP DISABLD type vfat (rw,nosuid,nodev,uhelper=udisks,uid=1000,gid=1000,shortname=mixed,dmask=0077,utf8=1,flush)
				volpath=$(mount | grep "^$disk " | cut -d' ' -f3- | cut -d'(' -f1)
				# volpath should be: /media/MBED type vfat
				if [ "$volpath" = "" ]; then
					echo "$disk is not mount. mount it first"
					sudo mount "$disk" /mnt
					sudo cp "$bin" /mnt
					sudo umount "$disk"
                    echo "Firmware update complete!"
                    break;
				else
					# Get the volume path from the mount command output
					# make volpath look like: /media/MBED
					volpath="${volpath:0:${#volpath} - 11}"

                    # Get volume label from mount command.
                    vollabel=$(mount -l | grep "^$disk " | cut -d'[' -f2- | cut -d']' -f1)
                    # desired result: MBED
                    echo "Volume label $vollabel"
                    if [ "$vollabel" != ${EXPECT_LABEL} ]; then
                        echo "Cannot flash device- it is code protected!"
                        # Left as an exercise to the reader- at this point the
                        # old firmware.bin file could be deleted and the user
                        # could be asked to remove and reinsert the device to
                        # reset code protect so it could be updated.
                    else
                        # copy the firmware to the mbed drive
                        cp "$bin" "$volpath"
                        echo "Firmware update complete!"

                        # unmount device when done to ensure that all of the
                        # data is written to the mbed board
                        umount "$disk"
                        echo "Device unmounted."
                        break
                    fi
				fi
			fi
		done
	fi
done


